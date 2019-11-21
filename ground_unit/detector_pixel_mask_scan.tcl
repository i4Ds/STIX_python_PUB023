##MASK Scan tcl script
#Pixel scan:
syslog "detector 4, pixel: 0 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  67108864 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector 4, pixel: 1 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  32768 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector 4, pixel: 2 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  256 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector 4, pixel: 3 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  2 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector 4, pixel: 4 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  536870912 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector 4, pixel: 5 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  262144 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector 4, pixel: 6 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  32 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector 4, pixel: 7 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  1 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector 4, pixel: 8 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  1073741824 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector 4, pixel: 9 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  2097152 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector 4, pixel: 10 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  2048 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector 4, pixel: 11 "
tcsend ZIX39005 {PIX00248 16 } {PIX00053  8 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "Detector scan:"
syslog "detector: 1"
tcsend ZIX39005 {PIX00248 1 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 2"
tcsend ZIX39005 {PIX00248 2 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 3"
tcsend ZIX39005 {PIX00248 4 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 4"
tcsend ZIX39005 {PIX00248 8 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 5"
tcsend ZIX39005 {PIX00248 16 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 6"
tcsend ZIX39005 {PIX00248 32 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 7"
tcsend ZIX39005 {PIX00248 64 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 8"
tcsend ZIX39005 {PIX00248 128 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 9"
tcsend ZIX39005 {PIX00248 256 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 10"
tcsend ZIX39005 {PIX00248 512 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 11"
tcsend ZIX39005 {PIX00248 1024 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 12"
tcsend ZIX39005 {PIX00248 2048 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 13"
tcsend ZIX39005 {PIX00248 4096 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 14"
tcsend ZIX39005 {PIX00248 8192 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 15"
tcsend ZIX39005 {PIX00248 16384 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 16"
tcsend ZIX39005 {PIX00248 32768 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 17"
tcsend ZIX39005 {PIX00248 65536 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 18"
tcsend ZIX39005 {PIX00248 131072 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 19"
tcsend ZIX39005 {PIX00248 262144 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 20"
tcsend ZIX39005 {PIX00248 524288 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 21"
tcsend ZIX39005 {PIX00248 1048576 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 22"
tcsend ZIX39005 {PIX00248 2097152 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 23"
tcsend ZIX39005 {PIX00248 4194304 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 24"
tcsend ZIX39005 {PIX00248 8388608 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 25"
tcsend ZIX39005 {PIX00248 16777216 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 26"
tcsend ZIX39005 {PIX00248 33554432 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 27"
tcsend ZIX39005 {PIX00248 67108864 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 28"
tcsend ZIX39005 {PIX00248 134217728 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 29"
tcsend ZIX39005 {PIX00248 268435456 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 30"
tcsend ZIX39005 {PIX00248 536870912 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 31"
tcsend ZIX39005 {PIX00248 1073741824 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
syslog "detector: 32"
tcsend ZIX39005 {PIX00248 2147483648 } {PIX00053  4294967295 } {PIX00054 100} checks {SPTV DPTV CEV} ack {ACCEPT COMPLETE}
waittime +10
#Total time to finish:440
