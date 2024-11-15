module cycler #(
    parameter DATA_WIDTH = 4, 
    parameter ADDR_WIDTH = 32
    paramater START_ADDR = 0,
) (
    input logic clk,
    input logic rst,
    input logic ready
    output logic [DATA_WIDTH-1:0] data, 
    output logic valid, 
    output logic [ADDR_WIDTH-1:0] addr_out
)


reg [ADDR_WIDTH-1:0][DATA_WIDTH-1:0] data_array = '{default:0};
assign addr_out = addr;
assign data = data_array[addr];

always_ff @(posedge clk) begin
    if (rst) begin
        addr <= START_ADDR;
        valid <= 0;
    end else if (ready) begin
        addr <= addr + 1;
        valid <= 1;
    end
end 
endmodule; // cycler