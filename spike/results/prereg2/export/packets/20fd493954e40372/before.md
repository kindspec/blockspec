---
layout: blog
title: "SELinux Volume Label Changes goes GA (and likely implications in v1.37)"
draft: true
date: 2026-04-29T10:30:00-08:00
slug: breaking-changes-in-selinux-volume-labeling
author: >
  [Jan Šafránek](https://github.com/jsafrane) (Red Hat)
  [Swathi Rao](https://github.com/SwathiR03) (independent)
---

If you run Kubernetes on Linux with SELinux in enforcing mode, plan ahead: a future release(anticipated to be v1.37) is
expected to turn the `SELinuxMount` feature gate on by default. This makes volume setup faster
for most workloads, but **it can break applications** that still depend on the older recursive relabeling
model in subtle ways (for example, sharing one volume between privileged and unprivileged Pods on the same node).
Kubernetes v1.36 is the right release to audit your cluster and fix or opt out of this change.

If your nodes do not use SELinux, or you use Windows workers, nothing changes for you: kubelet skips the whole
SELinux logic when SELinux is unavailable or disabled in the Linux kernel. You can skip this article completely.

<!--
  This is a direct copy from content/en/blog/_posts/2023/efficient-selinux-relabeling-beta.md.
  The problem is still the same. The old blog described SELinuxMountReadWriteOncePod feature gate,
  now we're expanding it to all volumes.

  Should we link it instead of copying? Rephrase it?
-->

## The problem

Linux systems with Security Enhanced Linux(SELinux)enabled use labels attached to objects (for example, files and network sockets) to make access control decisions. Traditionally, the container runtime applies SELinux labels to a Pod and all its volumes. Kubernetes only passes the SELinux label from a Pod's `securityContext` fields
to the container runtime.

The container runtime then recursively changes the SELinux label on all files that
are visible to the Pod's containers. This can be time-consuming if there are
many files on the volume, especially when the volume is on a remote filesystem.

{{% alert title="Note" color="info" %}}
If a container uses `subPath` of a volume, only that `subPath` of the whole
volume is relabeled. This allows two Pods that have two different SELinux labels
to use the same volume, as long as they use different subpaths of it.
{{% /alert %}}

If a Pod does not have any SELinux label assigned in the Kubernetes API, the
container runtime assigns a unique random label, so a process that potentially
escapes the container boundary cannot access data of any other container on the
host. The container runtime still recursively relabels all Pod volumes with this
random SELinux label.

## What Kubernetes is improving

Where the stack supports it, kubelet can mount the volume with `-o context=<label>` so the kernel
applies the correct label for all inodes on that mount without a recursive inode traversal. That path is
gated by feature flags and requires, among other things, that the Pod expose enough of an SELinux
label (for example `spec.securityContext.seLinuxOptions.level`) and that the volume driver opts in (for CSI,
CSIDriver field `spec.seLinuxMount: true`).

The project rolled this out in phases:

- ReadWriteOncePod volumes  were handled under the `SELinuxMountReadWriteOncePod` feature flag, on by default since v1.28 and GA in v1.36.
- Broader coverage was handled under the `SELinuxMount` flag, paired with the `spec.securityContext.seLinuxChangePolicy` field on Pods.

<!-- a heavily edited copy from the previous blog + docs in https://kubernetes.io/docs/tasks/configure-pod-container/security-context/ -->

If a Pod and its volume meet **all** of the following conditions, Kubernetes will
_mount_ the volume directly with the right SELinux label. Such a mount will happen
in a constant time and the container runtime will not need to recursively
relabel any files on it. For such a mount to happen: 

1. The operating system must support SELinux. Without SELinux support detected, kubelet and the container runtime do not
   do anything with regard to SELinux.

1. The [feature gate](/docs/reference/command-line-tools-reference/feature-gates/)
   `SELinuxMountReadWriteOncePod` must be enabled.
   The feature gate is GA in v1.36.

1. The Pod must use a `PersistentVolumeClaim` with applicable `accessModes` and [feature gates](/docs/reference/command-line-tools-reference/feature-gates/):
   * Either the volume has `accessModes: ["ReadWriteOncePod"]`, and feature gate `SELinuxMountReadWriteOncePod` is enabled.
   * Or the volume can use any other access modes and both feature gates
     `SELinuxChangePolicy` and `SELinuxMount` must be enabled
     and the Pod has `spec.securityContext.seLinuxChangePolicy` either nil (default) or `MountOption`.

   The feature gate `SELinuxMount` is Beta and disabled by default in Kubernetes 1.36,
   all others are GA.

   With any of these feature gates disabled, SELinux labels will always be
   applied by the container runtime via recursively traversing through the volume
   (or its subPaths).

1. The Pod must have at least `seLinuxOptions.level` assigned in its
   [Pod Security Context](/docs/reference/kubernetes-api/workload-resources/pod-v1/#security-context)
   or all Pod containers must have it set in their [Security Contexts](/docs/reference/kubernetes-api/workload-resources/pod-v1/#security-context-1).
   Kubernetes will read the default `user`, `role` and `type` from the operating
   system defaults (typically `system_u`, `system_r` and `container_t`).

   Without Kubernetes knowing at least the SELinux `level`, the container
   runtime will assign a random level _after_ the volumes are mounted. The
   container runtime will still relabel the volumes recursively in that case.

1. The volume plugin or the CSI driver responsible for the volume supports
   mounting with SELinux mount options.

   These in-tree volume plugins support mounting with SELinux mount options:
   `fc`, `iscsi`, and `rbd`.

   CSI drivers that support mounting with SELinux mount options must declare this capability in their
   [CSIDriver](/docs/reference/kubernetes-api/config-and-storage-resources/csi-driver-v1/)
   instance by setting the `seLinuxMount` field.

   Volumes managed by other volume plugins or CSI drivers that do not
   set `seLinuxMount: true` will be recursively relabeled by the container
   runtime.

## The breaking change

The `SELinuxMount` feature gate changes what volumes can be shared among multiple Pods in a subtle way.

Both of these cases work with recursive relabeling:

1. Two Pods with different SELinux labels share the same volume, but each of them uses a different `subPath` to the volume.
1. A privileged Pod and an unprivileged Pod share the same volume.

The above scenarios will  not work with the `SELinuxMount` option. One of these Pods will be stuck in `ContainerCreating` until the other Pod is terminated.

The first case is very niche and hasn't been seen in practice.
Although the second case is still quite rare, this setup has been observed in applications.
Kubernetes v1.36 offers metrics and events to identify these Pods and allows cluster administrators to opt out of the
mount option through the Pod field `spec.securityContext.seLinuxChangePolicy`.

### SELinuxChangePolicy

The new Pod field `spec.securityContext.seLinuxChangePolicy` specifies how the SELinux label is applied to all Pod volumes.
It is available when the feature gate `SELinuxChangePolicy` is enabled. The feature gate is enabled and GA in v1.36.

The field has three values:

* `nil` / not set (default): the SELinux label is applied recursively in v1.36, but it will be applied using the mount option when `SELinuxMount` is enabled and [all other conditions](#what-kubernetes-is-improving) are met. 
* `Recursive`: the SELinux label is applied recursively. This opts out from using the mount option.
* `MountOption`: the SELinux label is applied using the mount option, if [all other conditions](#what-kubernetes-is-improving)  are met. 
  This option is available only when the `SELinuxMount` feature gate is enabled.

### SELinuxWarningController

SELinuxWarningController is a new kube-controller-manager controller, available when the feature gate `SELinuxChangePolicy` is enabled.
It is an optional controller, as it does not have any use on clusters that do not support SELinux.
To enable the controller, pass `--controllers=*,selinux-warning-controller` on the kube-controller-manager command line.

The controller watches all Pods in the cluster and emits an event when it finds two Pods that share the same
volume in a way that is not compatible with the `SELinuxMount` feature gate.
All such conflicting Pods will receive an event like
*"SELinuxLabel "system_u:system_r:container_t:s0:c98,c99" conflicts with pod my-other-pod that uses the same volume as this pod with SELinuxLabel "system_u:system_r:container_t:s0:c0,c1". If both pods land on the same node, only one of them may access the volume."*
The actual Pod name may be censored when the conflicting Pods run in different namespaces to prevent leaking information across namespace boundaries.

The controller reports such an event even when these Pods don't run on the same node, to make sure all Pods work
regardless of the Kubernetes scheduler decision. They could run on the same node next time.

In addition, the controller emits the metric `selinux_warning_controller_selinux_volume_conflict` that lists all current conflicts among Pods.
The metric has labels that identify the conflicting Pods and their SELinux labels, such as:
```
selinux_warning_controller_selinux_volume_conflict{pod1_name="my-other-pod",pod1_namespace="default",pod1_value="system_u:object_r:container_file_t:s0:c0,c1",pod2_name="my-pod",pod2_namespace="default",pod2_value="system_u:object_r:container_file_t:s0:c0,c2",property="SELinuxLabel"} 1
```

The namespace names are always present in the metric. We assume only authorized personnel can access kube-controller-manager metrics.

### Suggested upgrade path

To ensure a smooth upgrade path from v1.36 to a release with `SELinuxMount` enabled (anticipated to be v1.37), te following procedure is suggested:

1. Enable SELinuxWarningController in the kube-controller-manager.
1. Check the `selinux_warning_controller_selinux_volume_conflict` metric. It shows all *potential* conflicts between Pods.
   For each conflicting Pod (Deployment, StatefulSet, ...), either apply the opt-out (set Pod's `spec.securityContext.seLinuxChangePolicy: Recursive`)
   or re-architect the application to remove such a conflict. For example, do your Pods really need to run as privileged?
1. Check the `volume_manager_selinux_volume_context_mismatch_warnings_total` metric. This metric is emitted by kubelet when it actually
   starts a Pod that runs when `SELinuxMount` is disabled, but such a Pod won't start when `SELinuxMount` is enabled.
 This metric lists the number of Pods that will experience a true conflict. Unfortunately, this metric does not expose the exact Pod name as a label.
   The full Pod name is available only in the `selinux_warning_controller_selinux_volume_conflict` metric.
1. Once both metrics have been accounted for, upgrade to a Kubernetes version that has `SELinuxMount` enabled.

Consider using a [MutatingAdmissionPolicy](/docs/reference/access-authn-authz/mutating-admission-policy/) to set the opt-out
in all Pods in a whole namespace or even in the whole cluster.

When `SELinuxMount` is enabled, kubelet will emit the metric `volume_manager_selinux_volume_context_mismatch_errors_total` with the number of
Pods that could not start because their SELinux label conflicts with an existing Pod that uses the same volume.
The exact Pod names should still be available in the `selinux_warning_controller_selinux_volume_conflict` metric,
if the SELinuxWarningController is enabled.

## Further reading

- KEP: [Speed up SELinux volume relabeling using mounts](https://github.com/kubernetes/enhancements/tree/master/keps/sig-storage/1710-selinux-relabeling)
- [SELinux Volume Relabeling Feature Gates](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#feature-gates)
- [Story 3: cluster upgrade](https://github.com/kubernetes/enhancements/tree/master/keps/sig-storage/1710-selinux-relabeling#story-3-cluster-upgrade)
- [Configure a security context for a Pod](/docs/tasks/configure-pod-container/security-context/) — Efficient SELinux volume relabeling and SELinuxWarningController

## Acknowledgements

If you run into issues, have feedback, or want to contribute, find us
on the Kubernetes Slack in `#sig-node` and `#sig-storage` or join a
[SIG Node](https://github.com/kubernetes/community/tree/main/sig-node) or [SIG Storage](https://github.com/kubernetes/community/tree/main/sig-storage) meetings.
