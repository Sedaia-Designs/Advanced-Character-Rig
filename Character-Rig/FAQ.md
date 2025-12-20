# FAQ

## Is there a release schedule? 

No, SACR is very much a passion project with no set deadlines. The work on the rig gets done at my liesure and when I feel an update is required.

## Can I request specific featuers?

Yes, although there is no guarentee your feature is included. To request a feature, please create an issue on the Github repository or in the [Discord Server](https://discord.gg/Qk4pfbG7Pf)

## What are the Experimental Builds?

Starting in Revision 4, a new Repository was setup called SACR Experimental. That repository focuses on experimenting with possible features, everything featured in Experimental Builds are subject to change. During the development of SACR R7, the repositories were merged, each major version gets it's own Release and Experimental Branch within a single repository.

Currently, any Indev version of SACR uses E instead of R to indicate that it is not a complete, stable rig. E labeled rigs are meant entirely for testing purposes and should only be used in testing environments to find bugs, test features, and test integration with Extensions.

## Will Revision 7 and future versions be backported to Blender 3.6 and older?

TL:DR, No, the work required to backport R7 and newer versions to Blender 3.X is just simply not worth my time, as 3.6 LTS ends June 2025 and as such, the 3.X series of Blender releases will no longer be updated.


For a more in-depth explaination, while Blender 3.6 is able to read a lot of the data from Blender 4 files, a multitude of issues occur due to the changes made to Armature Layers/Bone Groups, Geometry Nodes, and Custom Properties which cause Revision 7 to completely break when just doing a simple backport from Blender 4.4 to 3.3. The process to convert Bone Collections to Armature Layers is a very intensive process. While Drivers are preserved from 3.X -> 4.X, Drivers are deleted when going from 4.X -> 3.6. Furthermore, to prepare a 4.X rig for 3.5 and older requires work which is redundant.

I've already attempted a backport before by bringing SACR R4.1 to Blender 2.79, and looking back at that rig now it is very much broken to this day, and the issues faced then trying to port a rig from 2.8X to 2.79 was just too much of a hastle, especially now that I am not only developing SACR, but also the associated [Rig Interface Addon](https://sakura-sedaia.com/addon/sakura-rig-interface)

SACR is an open source project, while I won't backport R7 and newer to 3.X due to the ongoing development of Revision 8, the community is more than free to backport the rig themselves.
