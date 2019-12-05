+-----------------------------------------------------------------------------+
|                                                                             |
|  __   __   __      __   __     __   ___     __   ___  __          __   ___  |
| /__\ /__` '__\    /__` |__) | /  ` |__     /__` |__  |__) \  / | /  ` |__   |
| \__, .__/ \__/    .__/ |    | \__, |___    .__/ |___ |  \  \/  | \__, |___  |
|                                                                             |
|                                                                             |
+-----------------------------------------------------------------------------+

Welcome to the operational Solar Orbiter SPICE Kernel Dataset
=============================================================

     This directory contains the SPICE kernels Dataset generated for the
     SOLAR ORBITER mission.

     See more details in:

       http://www.cosmos.esa.int/web/spice/spice-for-solo

     To cite this SPICE Kernel Dataset in your publications please use:

        ESA SPICE Service, Solar Orbiter Operational SPICE Kernel Dataset,
        https://doi.org/10.5270/esa-kt1577e

     For more information on SPICE for ESA Planetary Missions, please go to

       http://www.cosmos.esa.int/web/spice

     For information on SPICE, please go to

       http://naif.jpl.nasa.gov

     For any question or suggestion on this site, please contact:

       ESA SPICE Service,      esa_spice@sciops.esa.int
       Marc Costa Sitja,       marc.costa@esa.int


Content of this directory
--------------------------------------------------------

     Each subdirectory within this directory contains all the kernels of
     the same type that have been generated for the SOLAR ORBITER Mission.

        ck:       Kernels that contain orientation for the spacecraft and
                  some of its structures, (solar arrays, for instance).

        fk:       Kernels that define reference frames needed for the
                  Mission.

        ik:       Kernels for the instruments on board the spacecraft.

        lsk:      Leapseconds kernel.

        mk:       Meta-kernel files (a.k.a "furnsh" files) that provide
                  lists of kernels suitable for a given mission period.

        pck:      Kernels that define planetary constants.

        sclk:     Spacecraft clock coefficients kernels.

        spk:      Orbit kernels, for the spacecraft and other solar system
                  bodies.


	   Please refer to the aareadme.txt in each of the subdirectories for
     information on the contents for the specific type of kernels and the
     corresponding naming conventions.


Usage of the SPICE Kernels for SOLAR ORBITER
--------------------------------------------------------

     At least a basic knowledge of the SPICE system is needed in order to
     use these kernels. The SPICE toolkit provides versions in Fortran
     (SPICELIB), C (CSPICE), IDL (icy), Matlab (mice) and Python (SpiceyPy),
     and the user can choose any one that suits him/her.

     The SPICELIB routine FURNSH, CSPICE function furnsh_c, icy routine
     cspice_furnsh and SpiceyPy routine furnsh load a kernel file into the
     kernel pool as shown below.

        CALL FURNSH  ( 'kernel_name' )
        furnsh_c     ( "kernel_name" );
        cspice_furnsh, 'kernel_name'
        cspice_funsh( 'kernel_name' );
        spiceypy.furnsh( 'kernel_name' )

     In the case when two or more files contain data overlapping in time
     for a given object, for binary kernels, the file loaded last takes
     precedence.

     If two (or more) text kernels assign value(s) using the '=' operator
     to identical keywords, the data value(s) associated with the last
     loaded occurrence of the keyword are used -all earlier values have
     been replaced with the last loaded value(s).

     An alternative to use this SPICE Kernel Dataset is to use the
     WebGeocalc Web Application (WGC):

        http://spice.esac.esa.int/webgeocalc/

     WGC provides a web-based graphical user interface to many of the
     observation geometry computations available from the SPICE system. A WGC
     user can perform SPICE computations without the need to write a program;
     the user need have only a computer with a standard web browser.


-------------------

     This file was created on July 4, 2019 by Marc Costa Sitja.


End of aareadme file.