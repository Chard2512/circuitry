module ALU (
    input [7:0] in1,
    input [7:0] in2,
    input [3:0] op,
    output [7:0] out
);

    always @(*) begin
        case (op)
            4'b0000: out = in1 + in2;
            4'b0001: out = in1 - in2;
            4'b0010: out = in1 * in2;
            4'b0011: out = in1 / in2;
            4'b0100: out = in1 % in2;
            4'b0101: out = in1 & in2;
            4'b0110: out = in1 | in2;
            4'b0111: out = in1 ^ in2;
            4'b1000: out = in1 ~& in2;
            4'b1001: out = in1 ~| in2;
            4'b1010: out = in1 ~^ in2;
            4'b1011: out = !in1;
            default: out = 0;
        endcase
    end

endmodule