## Constraints file for Nexys A7 XC7A100T-1CSG324C FPGA
## Maps the MIPS processor design to the Nexys A7 board based on schematic

## Clock signal (100 MHz)
set_property -dict { PACKAGE_PIN E3    IOSTANDARD LVCMOS33 } [get_ports { clk }]; # System clock
create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports { clk }];

## Reset signal (using CPU reset button)
set_property -dict { PACKAGE_PIN C12   IOSTANDARD LVCMOS33 } [get_ports { reset }]; # CPU Reset button (BTNRES)

## LEDs (16 LEDs: LD0 to LD15)
set_property -dict { PACKAGE_PIN T8   IOSTANDARD LVCMOS33 } [get_ports { led[0] }];  # LD0
set_property -dict { PACKAGE_PIN V9   IOSTANDARD LVCMOS33 } [get_ports { led[1] }];  # LD1
set_property -dict { PACKAGE_PIN R8   IOSTANDARD LVCMOS33 } [get_ports { led[2] }];  # LD2
set_property -dict { PACKAGE_PIN T6   IOSTANDARD LVCMOS33 } [get_ports { led[3] }];  # LD3
set_property -dict { PACKAGE_PIN T5   IOSTANDARD LVCMOS33 } [get_ports { led[4] }];  # LD4
set_property -dict { PACKAGE_PIN T4   IOSTANDARD LVCMOS33 } [get_ports { led[5] }];  # LD5
set_property -dict { PACKAGE_PIN U7   IOSTANDARD LVCMOS33 } [get_ports { led[6] }];  # LD6
set_property -dict { PACKAGE_PIN U6   IOSTANDARD LVCMOS33 } [get_ports { led[7] }];  # LD7
set_property -dict { PACKAGE_PIN V4   IOSTANDARD LVCMOS33 } [get_ports { led[8] }];  # LD8
set_property -dict { PACKAGE_PIN U3   IOSTANDARD LVCMOS33 } [get_ports { led[9] }];  # LD9
set_property -dict { PACKAGE_PIN V1   IOSTANDARD LVCMOS33 } [get_ports { led[10] }]; # LD10
set_property -dict { PACKAGE_PIN R1   IOSTANDARD LVCMOS33 } [get_ports { led[11] }]; # LD11
set_property -dict { PACKAGE_PIN P5   IOSTANDARD LVCMOS33 } [get_ports { led[12] }]; # LD12
set_property -dict { PACKAGE_PIN U1   IOSTANDARD LVCMOS33 } [get_ports { led[13] }]; # LD13
set_property -dict { PACKAGE_PIN R2   IOSTANDARD LVCMOS33 } [get_ports { led[14] }]; # LD14
set_property -dict { PACKAGE_PIN P2   IOSTANDARD LVCMOS33 } [get_ports { led[15] }]; # LD15

## 7-Segment Display
## Segments (CA, CB, CC, CD, CE, CF, CG) - Active low
set_property -dict { PACKAGE_PIN L3   IOSTANDARD LVCMOS33 } [get_ports { seg[0] }]; # CA
set_property -dict { PACKAGE_PIN N1   IOSTANDARD LVCMOS33 } [get_ports { seg[1] }]; # CB
set_property -dict { PACKAGE_PIN L5   IOSTANDARD LVCMOS33 } [get_ports { seg[2] }]; # CC
set_property -dict { PACKAGE_PIN L4   IOSTANDARD LVCMOS33 } [get_ports { seg[3] }]; # CD
set_property -dict { PACKAGE_PIN K3   IOSTANDARD LVCMOS33 } [get_ports { seg[4] }]; # CE
set_property -dict { PACKAGE_PIN M2   IOSTANDARD LVCMOS33 } [get_ports { seg[5] }]; # CF
set_property -dict { PACKAGE_PIN L6   IOSTANDARD LVCMOS33 } [get_ports { seg[6] }]; # CG

## Anodes (AN0 to AN3) - Active low
set_property -dict { PACKAGE_PIN M1   IOSTANDARD LVCMOS33 } [get_ports { an[0] }]; # AN0 (rightmost digit)
set_property -dict { PACKAGE_PIN L1   IOSTANDARD LVCMOS33 } [get_ports { an[1] }]; # AN1
set_property -dict { PACKAGE_PIN N4    IOSTANDARD LVCMOS33 } [get_ports { an[2] }]; # AN2
set_property -dict { PACKAGE_PIN N2   IOSTANDARD LVCMOS33 } [get_ports { an[3] }]; # AN3 (leftmost digit)

## Timing Constraints
## Ensure proper timing for the 7-segment display refresh
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

## Additional Settings
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]