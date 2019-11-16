
import random
import sys
import math
from myhdl import *


#print "Argument is ", sys.argv[1]  

def usage() :
    print """Usage: python gen_text_circuit input_text_file [mode]
          Mode may be  
              convert - create gen_text_circuit.v based on input_text_file  
              simulate - create RTL model and run simulation, reproducing input_text_file to stdout 
              all - both of the above [default]' """

def get_encoded_text(text) : 
   encoded_text = 0;
   for c in text[::-1] :  
       encoded_text <<= 8   
       encoded_text += ord(c)
       #print "Adding character", c ," with value " , ord(c), " to encoded_text, now has value ", encoded_text  
   return encoded_text

def extract_kb(encoded_text, kb_num) : 
    value = (encoded_text>>(kb_num*1024)) & (2**1024 -1)
    return value 

if (len(sys.argv) < 2):
    print("ERROR : at least 1 argument must be provided ") 
    print usage() 
    exit(1)  
elif  (len(sys.argv) == 2):
    mode = "all"
elif (len(sys.argv) == 3) :
    mode = sys.argv[2]
    if (mode != "convert" and mode != "all" and mode != "simulate" ): 
        print "ERROR : Invalid mode ", mode, " provided" 
        print usage() 
        exit(1)  
if (len(sys.argv) > 3 ): 
    print("ERROR : at most 2 arguments must be provided")  
    print usage() 
    exit(1)  

filename = sys.argv[1]
print "Reading and encoding ", filename, "..."
f= open(filename, "r")
text = f.read()
f.close()

width = int(math.ceil(math.log(len(text),2)))
num_bus =  (len(text)*8 / 1024) + 1
print "%File, ", filename,  " was read, it is ", len(text) , " characters long, counter will be ", width , " there will be ", num_bus , " 1024-bit text bus" 

encoded_text = get_encoded_text(text)
print "Done! File read and encoded numerically."

print "Starting to generate text_gen.v ..."
f= open("text_gen.v", "w")
f.write("""
module text_gen (
    input clk ,
    input reset,
    output [7:0] char 
);
""")

f.write("reg ["+str(width)+":0] count ;\n")
f.write("wire [1023:0] text_bus ["+str(num_bus)+"-1:0];\n")
f.write("wire [1023:0] active_bus;\n")
f.write("wire [6:0] char_idx;\n")
f.write("wire ["+str(width-7)+":0] bus_idx;\n")

for i in range(0,num_bus):
   f.write("assign text_bus["+str(i)+"] = 1024'd"+ str(extract_kb(encoded_text,i))  + "; \n")

f.write("assign char_idx = count[6:0];\n")
f.write("assign bus_idx  = count["+str(width)+":7];\n")
f.write("assign active_bus = text_bus[bus_idx];\n")
f.write("assign char       = active_bus[char_idx*8+7-:8];\n")

f.write("""
always @(posedge clk, negedge reset) begin: TEXT_GEN_SEQ
    if (reset == 0) begin
        count <= 0;
    end
    else begin
        count <= (count + 1);
    end
end

endmodule 
""")

f.close()
print "Done! text_gen.v created."

print "Starting to generate tb_text_gen.v ..."
f= open("tb_text_gen.v", "w")
f.write("""
module tb_text_gen;

reg clk;
reg reset;
wire [7:0] char;

always begin
   #5 clk = ~clk ;
end

always @( posedge clk) begin
   $write("%c", char);
end

initial begin
   $display("%% Starting to print character string from simulation... ");
   $dumpfile("tb_text_gen.vcd");
   $dumpvars(0, tb_text_gen);
   reset = 1'b0;
   clk = 1'b0;
   #6;
   reset = 1'b1;
""")

f.write("   #(10*"+str(len(text))+")") 

f.write("""
   $display("%% Finishing simulation.");
   $finish;
end
text_gen dut(
    clk,
    reset,
    char
);

endmodule

""")
print "Done! tb_text_gen.v created."

print "text_gen.py finished."

