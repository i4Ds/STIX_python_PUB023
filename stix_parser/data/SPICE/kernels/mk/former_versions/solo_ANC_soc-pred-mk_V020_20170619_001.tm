KPL/MK

Meta-kernel for the Solar Orbiter dataset v0.2.0 -- Predicted 20170706_001
==========================================================================

   This meta-kernel lists the Solar Orbiter SPICE kernels providing
   information for the full mission based on predicted and test data.


Usage of the Meta-kernel
-------------------------------------------------------------------------

   This meta-kernel lists the Solar Orbiter SPICE kernels providing the
   following coverage:

      Summary for: ../spk/solo_ANC_soc-orbit-crema-4-0-in_20190214-20290611_V01.bsp

      Body: SOLAR ORBITER (-144)
            Start of Interval (ET)              End of Interval (ET)
            -----------------------------       -----------------------------
            2019 FEB 14 18:00:00.000            2029 JUN 11 05:50:21.120


      Summary for: ../ck/solo_ANC_soc-default-att_20190214-20290611_V01.bc

      Object:  -144000
        Interval Begin ET        Interval End ET          AV
        ------------------------ ------------------------ ---
        2019-FEB-14 17:59:59.999 2029-JUN-11 05:48:59.999 Y


   Reading the comments of the binary SPK and C-Kernels is very helpful to
   understand the implemented SC position and orientation. You can use the
   following NAIF command line utility to extract that information from the
   kernels:

      > commnt -r solo_ANC_soc-*.bc

   The kernels listed below can be obtained from the ESA SPICE FTP server:

      ftp://spiftp.esac.esa.int/data/SPICE/SOLAR-ORBITER/kernels/


Implementation Notes
-------------------------------------------------------------------------

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the SOLAR-ORBITER SPICE data set's ``data'' directory on
   their system. Replacing ``/'' with ``\'' and converting line
   terminators to the format native to the user's system may also be
   required if this meta-kernel is to be used on a non-UNIX workstation.

-------------------

   This file was created on June 19, 2017 by Marc Costa Sitja (ESAC/ESA).


   \begindata

       PATH_VALUES     = ( '../..')

       PATH_SYMBOLS    = ( 'KERNELS')

       KERNELS_TO_LOAD = (

          '$KERNELS/../former_versions/misc'
          'solo_ANC_soc-sc-boom-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-sc-fof-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-eui-fsi-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-eui-hri-euv-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-eui-hri-lya-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-metis-euv-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-metis-vis-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-metis-m0-tel-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-phi-fdt-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-phi-hrt-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-solohi-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-spice-sw-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-spice-lw-ck_20180930-21000101_V01.bc'
          '$KERNELS/ck/solo_ANC_soc-stix-ck_20180930-21000101_V01.bc'

          '$KERNELS/../former_versions/misc'
          'solo_ANC_soc-default-att_20190214-20290611_V01.bc'


          '$KERNELS/fk/solo_ANC_soc-sc-fk_V01.tf'
          '$KERNELS/fk/solo_ANC_soc-ops-fk_V01.tf'
          '$KERNELS/fk/solo_ANC_soc-sci-fk_V00.tf'
          '$KERNELS/fk/earth_topo_050714.tf'
          '$KERNELS/fk/estrack_v01.tf'


          '$KERNELS/ik/solo_ANC_soc-epd-ik_V01.ti'
          '$KERNELS/ik/solo_ANC_soc-eui-ik_V00.ti'
          '$KERNELS/ik/solo_ANC_soc-metis-ik_V00.ti'
          '$KERNELS/ik/solo_ANC_soc-phi-ik_V00.ti'
          '$KERNELS/ik/solo_ANC_soc-solohi-ik_V00.ti'
          '$KERNELS/ik/solo_ANC_soc-spice-ik_V00.ti'
          '$KERNELS/ik/solo_ANC_soc-stix-ik_V00.ti'
          '$KERNELS/ik/solo_ANC_soc-str-ik_V00.ti'
          '$KERNELS/ik/solo_ANC_soc-swa-ik_V01.ti'


          '$KERNELS/lsk/naif0012.tls'


          '$KERNELS/pck/earth_070425_370426_predict.bpc'
          '$KERNELS/pck/pck00010.tpc'


          '$KERNELS/sclk/solo_ANC_soc-sclk-fict_20000101_V01.tsc'


          '$KERNELS/../former_versions/misc'
          'solo_ANC_soc-orbit_20190214-20290611_V01.bsp'

          '$KERNELS/spk/de421.bsp'
          '$KERNELS/spk/estrack_v01.bsp'

                       )

   \begintext


End of MK file.
