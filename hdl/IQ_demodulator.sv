module demodulator #
  (
    parameter DATA_WIDTH = 4 + 8 + 32, 
  )
  (
    inpu logic clk, 
    input logic rst,
    input logic [DATA_WIDTH-1:0] data_in,
    input logic valid_in,
    input logic ready_in, 
    output logic valid_out,
    output logic ready_out,
    
    output logic [DATA_WIDTH-1:0] data_out
  );
 
  logic signed [C_S00_AXIS_TDATA_WIDTH - 1 : 0] valid_data; 
  assign s00_axis_tready = m00_axis_tready || ~m00_axis_tvalid;
  logic signed [15:0] amp_out;
  sine_generator #(.PHASE(PHASE)) sine_inst(.clk_in(clk), 
                                            .rst_in(rst_in), 
                                            .step_in(1'b1), 
                                            .amp_out(amp_out));
  
  always_ff @(posedge clk) begin 
    if (rst)begin
      m00_axis_tdata <= 0; 
      m00_axis_tvalid <= 0;
      m00_axis_tlast <= 0;
      // CALIBRATION HERE
      // lower ready when calibrating, do on reset and on each packet or two...
    end else begin
      if (s00_axis_tready && s00_axis_tvalid) begin 
        m00_axis_tdata <= $signed(amp_out) * $signed(valid_data);
        m00_axis_tvalid <= s00_axis_tvalid;
        m00_axis_tlast <= s00_axis_tlast;
        m00_axis_tstrb <= 4'b1111;
      end 
    end 
  end 
endmodule




