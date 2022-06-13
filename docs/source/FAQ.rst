Frequently Asked Questions
---------------------------

**Singularity and my local environments**

Bind mounts partitions to the Singularity environment using ``--singularity-args '--bind $YOURMOUNTDISK'``. It allows to detect non-standard mountpoint into the Singularity container. $YOURMOUNTDISK corresponds to the requested partition or volume, and it could be $HOME or another mount path.
