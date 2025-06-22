# MIPS Processor

## Overview
A quick summary of the project is provided below. For a complete description of working and functionality, please refer to the attached detailed report.

## Summary
The Complex Engineering Problem (CEP) outlined in the document focuses on the design and 
implementation of a single-cycle MIPS processor on the Nexys A7 FPGA board. This project 
integrates fundamental concepts of digital systems design, computer architecture, and hardware 
description languages to create a functional processor capable of executing a subset of the MIPS 
Instruction Set Architecture (ISA). The primary objective is to develop a synthesizable Verilog 
implementation of a single-cycle MIPS processor that can execute R-type (add, sub, and, or, slt), 
I-type (addi, lw, sw, beq), and J-type (j) instructions, utilizing the Nexys A7s on-board memory, 
LEDs, and 7-segment displays for instruction storage, status indication, and result visualization. 
The processor must operate within a single clock cycle for all instructions, necessitating careful 
consideration of the critical path to ensure timing constraints are met. The design process 
emphasizes modular Verilog coding practices to enhance readability and maintainability, with 
distinct modules for the control unit, ALU, register file, and memory.
