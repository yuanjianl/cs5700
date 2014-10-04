import java.io.IOException;
import java.lang.InterruptedException;

public class Experiment1 extends Experiment {

    private String[] TCP_KIND = {"Tahoe", "Reno", "NewReno", "Vegas"};
    private int[] CBR_RATE = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    // Variables for calculating.

    // For throughput, I used the packet received at the end node to calculate.
    private int left_to_right_bytes;
    private int right_to_left_bytes;

    // For drop rate, I simply use the largest global packet number as the
    // total number of sent packet. The number of dropped packet are calculated
    // as number of d.
    private int totalPacketSent;
    private int totalPacketDropped;

    // For latency, I used a float[] to hold all sent time. The init value is -1.0f;
    private float[] tcp_packet_sent_time;
    private double total_latency;
    private int total_received_tcp_at_3;

    public Experiment1() {
        initAllCalculatingValues();
    }

    protected void getFeed(String line) {
        String[] trace = line.split(" ");

        int globalPacketNumber = Integer.parseInt(trace[trace.length - 1]);
        if ( globalPacketNumber > totalPacketSent ) {
            totalPacketSent = globalPacketNumber;
        }
        String messageType = trace[MESSAGE_TYPE];
        if ( messageType.equals(DROPPED) ) {
            totalPacketDropped += 1;
        }
        // If it's a DEQUEUED message at node 0, it is a tcp out packet.
        else if ( messageType.equals(DEQUEUED) && trace[SENDER].equals("0") ) {
            float time = Float.parseFloat(trace[TIME]);
            int seqNum = Integer.parseInt(trace[trace.length - 2]);

            // If the current float[] is not big enough, double it.
            if (seqNum >= tcp_packet_sent_time.length ) {
                increaseArraySize();
            }

            if (tcp_packet_sent_time[seqNum] == INIT_SENT_TIME){
                tcp_packet_sent_time[seqNum] = time;
            }
        } else if ( messageType.equals(RECEIVED) ) {
            if ( trace[RECEIVER].equals("3")) {
                if ( trace[PACKET_TYPE].equals(TCP) ) {
                    float time = Float.parseFloat(trace[TIME]);
                    int seqNum = Integer.parseInt(trace[trace.length - 2]);
                    
                    // If the sent time is -1.0, there is an error. Ignore it.
                    if (tcp_packet_sent_time[seqNum] != INIT_SENT_TIME) {
                        total_latency += time - tcp_packet_sent_time[seqNum];
                        total_received_tcp_at_3 += 1;
                        tcp_packet_sent_time[seqNum] = INIT_SENT_TIME;
                    }
                }

                left_to_right_bytes += Integer.parseInt(trace[PACKET_SIZE]);
            } else if (trace[RECEIVER].equals("2") && trace[PACKET_TYPE].equals(CBR)) {
                left_to_right_bytes += Integer.parseInt(trace[PACKET_SIZE]);
            } else if ( trace[RECEIVER].equals("0") ) {
                right_to_left_bytes += Integer.parseInt(trace[PACKET_SIZE]);
            }
        }
    }

    protected String result() {
        StringBuilder sb = new StringBuilder();

        System.out.println("Left to right bytes is: " + left_to_right_bytes);
        System.out.println("Right to left bytes is: " + right_to_left_bytes);
        System.out.println("Total Throughput is: " + 8.0 * (left_to_right_bytes + right_to_left_bytes) / (10 * 1000 * 1000) + "Mbps");

        System.out.println("Total Packet Sent is: " + totalPacketSent);
        System.out.println("Total Packet Dropped is: " + totalPacketDropped);
        sb.append("The drop rate is: " + 1.0 * totalPacketDropped / totalPacketSent);

        System.out.println("TCP stream latency is: " + total_latency / total_received_tcp_at_3);
        System.out.println("There are " + getLostPackets() + " lost.");

        initAllCalculatingValues();
        return sb.toString();
    }

    private int getLostPackets(){
        int result = 0;
        for (int i = 0 ; i < tcp_packet_sent_time.length ; i ++){
            if ( tcp_packet_sent_time[i] != INIT_SENT_TIME ){
                result += 1;
            }
        }
        return result;
    }

    private void increaseArraySize() {
        float[] temp = new float[tcp_packet_sent_time.length * 2];
        for (int i = 0 ; i < tcp_packet_sent_time.length ; i ++) {
            temp[i] = tcp_packet_sent_time[i];
        }
        tcp_packet_sent_time = temp;
    }

    protected void initAllCalculatingValues() {
        left_to_right_bytes = 0;
        right_to_left_bytes = 0;

        totalPacketSent = 0;
        totalPacketDropped = 0;

        tcp_packet_sent_time = new float[ESTIMATED_TCP_PACKET_NUMBER];
        for (int i = 0 ; i < tcp_packet_sent_time.length ; i ++) {
            tcp_packet_sent_time[i] = INIT_SENT_TIME;
        }

        total_latency = 0.0;
        total_received_tcp_at_3 = 0;
    }

    public void start() {
        for (int i = 0 ; i < TCP_KIND.length ; i ++) {
            for (int j = 0; j < CBR_RATE.length ; j++ ) {
                CBR_RATE[j] = 10;
                String shellScript = "/course/cs4700f12/ns-allinone-2.35/bin/ns experiment1.tcl " + TCP_KIND[i] + " " + CBR_RATE[j];
                try {
                    Runtime.getRuntime().exec(shellScript);
                    Thread.sleep(5000);
                } catch (IOException ex) {
                    ex.printStackTrace();
                } catch (InterruptedException ex) {
                    ex.printStackTrace();
                }
                readFile("my_experimental1_output_" + TCP_KIND[i] + "_" + CBR_RATE[j] + ".tr");
                break;
            }
            break;
        }
    }

    public static void main(String[] args) {
        Experiment1 ex1 = new Experiment1();
        ex1.start();
    }
}