KPL/FK

Frame (FK) kernel file for SOLO Spacecraft Ecliptical-Normal Pointing 
===============================================================================

   This frames kernel overwrites the SOLO spacecraft frame (SOLO_PRF)
   definition from [3] and maps it to the SOLO Ecliptical-NORM pointing @ Sun
   frame (SOLO_ECLIP_NORM) defined in [4].
   
   This allows the user to use the existing alignments and instrument frame
   definitions in the SOLO frames kernel (see ref [3]) to perform instrument
   specific mission analysis and attitude dependent science opportunity
   identification. Please refer to the section ``Using this frame'' for further
   details.
   
   NOTE THAT BY USING THIS KERNEL, THE SOLO_SPACECRAFT FRAME WILL BE 
   MAPPED TO THE SOLO_ECLIP_NORM FRAME, AND ANY CK PROVIDING
   ORIENTATION FOR THE SOLO_SPACECRAFT FRAME WILL NOT BE USED BY THE
   APPLICATION SOFTWARE, EVEN IF IT IS LOADED IN THE KERNEL POOL.
   
   
Version and Date
-------------------------------------------------------------------------------
      
   Version 0.0 -- June 19, 2017 -- Marc Costa Sitja, ESAC/ESA
   
      Initial version.   

References
-------------------------------------------------------------------------------

   1.   ``Frames Required Reading''
   
   2.   ``Kernel Pool Required Reading''
   
   3.   SOLO Frames Definition Kernel (FK), latest version.
   
   4.   SOLO Science Operations Frames Definition Kernel (FK), latest
        version.

         
Contact Information
-------------------------------------------------------------------------------

   If you have any questions regarding this file contact SPICE support at
   ESAC:

           Marc Costa Sitja
           (+34) 91-8131-457
           mcosta@sciops.esa.int, esa_spice@sciops.esa.int
           
   or the Solar Orbiter Science Operations Center at ESAC:

           sol_soc@esa.int
           

Implementation Notes
-------------------------------------------------------------------------------

   This file is used by the SPICE system as follows: programs that make use
   of this frame kernel must "load" the kernel normally during program
   initialization. Loading the kernel associates the data items with
   their names in a data structure called the "kernel pool".  The SPICELIB
   routine FURNSH loads a kernel into the pool as shown below:
 
     FORTRAN: (SPICELIB)
 
       CALL FURNSH ( frame_kernel_name )
 
     C: (CSPICE)
 
       furnsh_c ( frame_kernel_name );
 
     IDL: (ICY)
 
       cspice_furnsh, frame_kernel_name
 
     MATLAB: (MICE)
       
          cspice_furnsh ( 'frame_kernel_name' )
 
     PYTHON: (SPICEYPY)*
 
       furnsh( frame_kernel_name )
 
   In order for a program or routine to extract data from the pool, the
   SPICELIB routines GDPOOL, GIPOOL, and GCPOOL are used.  See [2] for
   more details.
 
   This file was created and may be updated with a text editor or word
   processor.
 
   * SPICEPY is a non-official, community developed Python wrapper for the
     NAIF SPICE toolkit. Its development is managed on Github.
     It is available at: https://github.com/AndrewAnnex/SpiceyPy
   

Using this frame
-------------------------------------------------------------------------------

   This frames have been implemented to overwrite the SOLO_PRF
   frame definition provided in the SOLO Frames Definitions kernel ([3])
   and map it to the SOLO_ECLIP_NORM frame defined in the SOLO
   Science Operations Frames Definitions kernel ([4]).
   
   In order to make use of this frames kernel, this file MUST BE LOADED
   AFTER the SOLO frames definition kernel and the SOLO Science Operations
   Frames Definition kernel.
   
   A metakernel defined to use this file should look like this:
      
         ...
         
              $DATA/fk/solo_ANC_soc-sc-fk_V00.tf
              $DATA/fk/solo_ANC_soc-sc-fk_V00.tf
              $DATA/fk/solo_sc_orb_norm_v00.tf
         
         ...
         
   (*) the example presents version 0.0 of the SOLO frames and
       SOLO Science Operations frames kernels. Newer versions of
       these files will produce the same results. 
   
   NOTE THAT BY USING THIS KERNEL, THE SOLO_PRF FRAME WILL BE 
   MAPPED TO THE SOLO_ECLIP_NORM FRAME, AND ANY CK PROVIDING
   ORIENTATION FOR THE SOLO_SPACECRAFT FRAME WILL NOT BE USED BY THE
   APPLICATION SOFTWARE, EVEN IF IT IS LOADED IN THE KERNEL POOL.


  \begindata
  
      FRAME_-144000_CLASS        = 4
      TKFRAME_-144000_RELATIVE   = 'SOLO_ECLIP_NORM'
      TKFRAME_-144000_SPEC       = 'MATRIX'
      TKFRAME_-144000_MATRIX     = ( 1   0   0
                                     0   1   0
                                     0   0   1 )
   
  \begintext


End of FK file.