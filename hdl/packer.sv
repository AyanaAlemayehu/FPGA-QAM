module packer #(
    parameter DATA_WIDTH = 4, 
    parameter ADDR_WIDTH = 32
    paramater START_ADDR = 0,
    parameter PACK_WIDTH = 8 + ADDR_WIDTH
) (
    input logic clk,
    input logic rst,
    input logic ready_in,
    input logic addr, 
    output logic valid_out, 
    output logic ready_out,
    input logic valid_in, 
    input logic [DATA_WIDTH-1:0] data_in,
    output logic [DATA_WIDTH + PACK_WIDTH - 1:0] data_out
) 

always_ff @(posedge clk) begin
    if (rst) begin
        data_out <= 0;
        ready_out <= 0;
        valid_out <= 0;
    end else if (ready_in) begin
        data_out <= {4'b1111, addr, data_in, 4'b0101};
        ready_out <= 1;
        valid_out <= 1;
    end else if (valid_in) begin
        ready_out <= 0;
        valid_out <= 0;
    end
end 
endmodule; // packer