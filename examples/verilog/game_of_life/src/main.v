`default_nettype none

module rule (
    input [7:0] neigh,
    input current,
    output next );

    wire [2:0] pop;
    assign pop = {2'b00, neigh[0]} +
                 {2'b00, neigh[1]} +
                 {2'b00, neigh[2]} +
                 {2'b00, neigh[3]} +
                 {2'b00, neigh[4]} +
                 {2'b00, neigh[5]} +
                 {2'b00, neigh[6]} +
                 {2'b00, neigh[7]}; 
    
    reg tmp;
    assign next = tmp;

    always @(*) begin
        case (pop)
            2: tmp = current;
            3: tmp = 1;
            default: tmp = 0;
        endcase
    end
endmodule

// The auto_place function requires matrices to separated into rows,
// in order to build them as matrices, that's why the matricies are ugly 
// defined like this. This is something that will change.
module life ( 
    input [7:0] data0,
    input [7:0] data1,
    input [7:0] data2,
    input [7:0] data3,
    input [7:0] data4,
    input [7:0] data5,
    input [7:0] data6,
    input [7:0] data7,
    input clk,
    input load,
    output reg [7:0] q0,
    output reg [7:0] q1,
    output reg [7:0] q2,
    output reg [7:0] q3,
    output reg [7:0] q4,
    output reg [7:0] q5,
    output reg [7:0] q6,
    output reg [7:0] q7
); 

    wire [63:0] data = {data0, data1, data2, data3, data4, data5, data6, data7};
    wire [63:0] q = {q0, q1, q2, q3, q4, q5, q6, q7};

    wire [63:0] next;
    
    genvar x, y;
    generate
        for (x=0; x<=7; x=x+1) begin : gen_x
            for (y=0; y<=7; y=y+1) begin : gen_y
                rule fate (
                    .neigh({q[(x==0 ? 7 : x-1) + (y==0 ? 7 : y-1)*8],
                            q[(x==0 ? 7 : x-1) + y                *8],
                            q[(x==0 ? 7 : x-1) + (y==7 ? 0 : y+1)*8],
                            q[x                 + (y==0 ? 7 : y-1)*8],
                            q[x                 + (y==7 ? 0 : y+1)*8],
                            q[(x==7 ? 0 : x+1) + (y==0 ? 7 : y-1)*8],
                            q[(x==7 ? 0 : x+1) + y                *8],
                            q[(x==7 ? 0 : x+1) + (y==7 ? 0 : y+1)*8]}),
                    .current(q[(x + y*8)]),
                    .next(next[(x + y*8)])
                );
            end
        end
    endgenerate
    
    always @(posedge clk) begin
        if (load) begin
            {q0, q1, q2, q3, q4, q5, q6, q7} <= data;
        end else begin
            {q0, q1, q2, q3, q4, q5, q6, q7} <= next;
        end
    end
endmodule