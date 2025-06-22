// Top-level module
module mips_processor (
    input wire clk,               // Clock input
    input wire reset,             // Reset input
    output wire [15:0] led,       // LEDs for status
    output wire [6:0] seg,        // 7-segment display segments
    output wire [3:0] an          // 7-segment display anodes
);
    // Internal signals
    wire [31:0] pc, instr, alu_result, write_data, read_data1, read_data2, imm_ext, branch_target, jump_target;
    wire [31:0] mem_data, next_pc;
    wire [4:0] write_reg;
    wire [3:0] alu_control;
    wire reg_dst, alu_src, mem_to_reg, reg_write, mem_write, branch, jump, zero;
    wire [15:0] display_data;
    wire [31:0] t3_data;

    // Program Counter
    reg [31:0] pc_reg;
    always @(posedge clk or posedge reset) begin
        if (reset)
            pc_reg <= 32'h00000000;
        else
            pc_reg <= next_pc;
    end
    assign pc = pc_reg;

    // Instruction Memory
    instruction_memory instr_mem (
        .addr(pc[9:2]),
        .instr(instr)
    );

    // Control Unit
    control_unit ctrl (
        .opcode(instr[31:26]),
        .funct(instr[5:0]),
        .reg_dst(reg_dst),
        .alu_src(alu_src),
        .mem_to_reg(mem_to_reg),
        .reg_write(reg_write),
        .mem_write(mem_write),
        .branch(branch),
        .jump(jump),
        .alu_control(alu_control)
    );

    // Register File
    register_file reg_file (
        .clk(clk),
        .we(reg_write),
        .ra1(instr[25:21]),
        .ra2(instr[20:16]),
        .wa(write_reg),
        .wd(write_data),
        .rd1(read_data1),
        .rd2(read_data2)
    );

    // Read $t3 (register $11) directly for display
    wire [31:0] t3_read;
    register_file reg_file_display (
        .clk(clk),
        .we(1'b0),                // No write for this instance
        .ra1(5'd11),              // Read $t3
        .ra2(5'd0),               // Unused
        .wa(5'd0),                // Unused
        .wd(32'd0),               // Unused
        .rd1(t3_data),            // $t3 value
        .rd2()                    // Unused
    );

    // Immediate Extension
    assign imm_ext = {{16{instr[15]}}, instr[15:0]}; // Sign-extend 16-bit immediate

    // ALU Source Mux
    wire [31:0] alu_src_b = alu_src ? imm_ext : read_data2;

    // ALU
    alu alu_inst (
        .a(read_data1),
        .b(alu_src_b),
        .alu_control(alu_control),
        .result(alu_result),
        .zero(zero)
    );

    // Data Memory
    data_memory data_mem (
        .clk(clk),
        .we(mem_write),
        .addr(alu_result[9:2]),
        .wd(read_data2),
        .rd(mem_data)
    );

    // Write Register Mux
    assign write_reg = reg_dst ? instr[15:11] : instr[20:16];

    // Write Data Mux
    assign write_data = mem_to_reg ? mem_data : alu_result;

    // Branch and Jump Logic
    assign branch_target = pc + 4 + (imm_ext << 2);
    assign jump_target = {pc[31:28], instr[25:0], 2'b00};
    assign next_pc = jump ? jump_target : (branch && zero ? branch_target : pc + 4);

    // LED Status
    assign led = {14'b0, reset, ~reset}; // Fixed: LED[1] = reset, LED[0] = running

    // 7-Segment Display: Show $t3's value after program execution
    assign display_data = (pc >= 32'h00000014) ? t3_data[15:0] : read_data1[15:0];
    seven_segment_display ssd (
        .clk(clk),
        .reset(reset),
        .data(display_data),
        .seg(seg),
        .an(an)
    );

endmodule