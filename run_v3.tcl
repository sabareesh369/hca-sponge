# run_v3.tcl - Keccak baseline, HCA-24 (32-bit port), HCA-12 (64-bit port)
# Timing is constrained close to each design's Fmax so that timing is MET.
# Power is reported at 100 MHz for every design with the same method.
# Usage (Vivado 2025.2 Tcl Shell):  cd C:/Users/Sabar/hca_v3   then   source run_v3.tcl
set BASE [pwd]
set OUT  "$BASE/reports_v3"
file mkdir $OUT
# name  top  folder  files  period(xc7a200t)  period(xc7a100t)
set designs [list \
  [list keccak   keccak    keccak_orig [list keccak.v f_permutation.v round.v padder.v padder1.v rconst.v] 5.0 6.3] \
  [list hca24    keccak_ca hca24       [list keccak_ca.v f_permutation_ca.v round_ca_pi.v padder.v padder1.v rconst.v] 9.3 10.6] \
  [list hca12_64 keccak_ca hca12_64    [list keccak_ca.v f_permutation_ca.v round_ca_pi.v padder.v rconst.v] 9.3 10.8] ]
set parts [list xc7a200tfbg676-2 xc7a100tcsg324-1]
set summary [open "$OUT/summary.csv" w]
puts $summary "design,part,period_ns,WNS_ns,timing_met,Fmax_MHz,crit_path_ns,logic_levels"
foreach d $designs {
  lassign $d name top dir files p200 p100
  foreach part $parts {
    if {$part eq "xc7a200tfbg676-2"} {set P $p200} else {set P $p100}
    close_project -quiet
    create_project -in_memory -part $part
    foreach f $files { read_verilog "$BASE/$dir/$f" }
    synth_design -top $top -part $part -mode out_of_context -flatten_hierarchy rebuilt
    create_clock -name clk -period $P [get_ports clk]
    opt_design
    place_design
    route_design
    set tag "${name}_${part}"
    report_utilization    -file "$OUT/${tag}_util.rpt"
    report_timing_summary -file "$OUT/${tag}_timing.rpt" -max_paths 5
    set p   [lindex [get_timing_paths -max_paths 1 -setup] 0]
    set wns [get_property SLACK $p]
    set met [expr {$wns >= 0 ? "yes" : "no"}]
    set fmax [expr {1000.0 / ($P - $wns)}]
    puts $summary "$name,$part,$P,$wns,$met,[format %.1f $fmax],[get_property DATAPATH_DELAY $p],[get_property LOGIC_LEVELS $p]"
    flush $summary
    create_clock -name clk -period 10.000 [get_ports clk]
    report_power -file "$OUT/${tag}_power100.rpt"
  }
}
close $summary
puts "DONE - zip and send the folder: $OUT"
