import java.io.IOException;
import java.lang.InterruptedException;

public class Experiment2 extends Experiment {

    private String[] TCP_KIND = {"Tahoe", "Reno", "NewReno", "Vegas"};
    private int[] CBR_RATE = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    // Variables for recording.
    private int firstTCP;
    private int secondTCP;
    private int j = CBR_RATE.length;
    private float[][] throughputs = new float[j][2];
    private float[][] delays = new float[j][2];
    private float[][] dropRates = new float[j][2];

    // Variables for calculating.

    // For throughput, I used the packet received at the end node to calculate.
    private int[] total_bytes;

    // For drop rate, I simply use the largest global packet number as the
    // total number of sent packet. The number of dropped packet are calculated
    // as number of d.
    private int[] totalPacketSent;
    private int[] totalPacketDropped;
    private int[] totalPacketReceived;

    // For latency, I used a float[] to hold all sent time. The init value is -1.0f;
    private float[][] tcp_packet_sent_time;
    private float[] total_latency;

    public Experiment2(int firstTCP, int secondTCP) {
        initAllCalculatingValues();
        this.firstTCP = firstTCP;
        this.secondTCP = secondTCP;
    }

    protected void getFeed(String line) {
        String[] trace = line.split(" ");

        String messageType = trace[MESSAGE_TYPE];
        int flow_id = Integer.parseInt(trace[FLOW_ID]) - 1;
        if ( messageType.equals(DROPPED) && trace[PACKET_TYPE].equals(TCP)) {
            totalPacketDropped[flow_id] += 1;
        }
        // If it's a DEQUEUED message at node 0, it is a tcp out packet.
        else if ( messageType.equals(DEQUEUED) && (trace[SENDER].equals("0") || trace[SENDER].equals("4"))) {
            totalPacketSent[flow_id] += 1;

            float time = Float.parseFloat(trace[TIME]);
            int seqNum = Integer.parseInt(trace[trace.length - 2]);

            // If the current float[] is not big enough, double it.
            if (seqNum >= tcp_packet_sent_time[flow_id].length ) {
                increaseArraySize();
            }

            if (tcp_packet_sent_time[flow_id][seqNum] == INIT_SENT_TIME) {
                tcp_packet_sent_time[flow_id][seqNum] = time;
            }
        } else if ( messageType.equals(RECEIVED) ) {
            if ( (trace[RECEIVER].equals("0")) || trace[RECEIVER].equals("4") && trace[PACKET_TYPE].equals(ACK) ) {
                float time = Float.parseFloat(trace[TIME]);
                int seqNum = Integer.parseInt(trace[trace.length - 2]);

                // If the sent time is -1.0, there is an error. Ignore it.
                if (tcp_packet_sent_time[flow_id][seqNum] != INIT_SENT_TIME) {
                    total_latency[flow_id] += time - tcp_packet_sent_time[flow_id][seqNum];
                    totalPacketReceived[flow_id] += 1;
                    total_bytes[flow_id] += 1040;
                    tcp_packet_sent_time[flow_id][seqNum] = INIT_SENT_TIME;
                }
            }
        }
    }

    protected void result() {
        getLostPackets();

        // System.out.println("Total packet sent: " + totalPacketSent[0] + " " + totalPacketSent[1]);

        for (int i = 0 ; i < 2 ; i ++) {
            float throuput = 8.0f * (total_bytes[i]) / (10 * 1000 * 1000);
            float delay = 1000.0f * total_latency[i] / totalPacketReceived[i];
            float dropRate = 100.0f * (totalPacketSent[i] - totalPacketReceived[i]) / totalPacketSent[i];

            // System.out.println("Throughput is: " + throuput);
            // System.out.println("Delay is: " + delay);
            // System.out.println("Drop rate is: " + dropRate);

            throughputs[j][i] = throuput;
            delays[j][i] = delay;
            dropRates[j][i] = dropRate;
        }

        initAllCalculatingValues();
    }

    private void getLostPackets() {
        for (int i = 0; i < 2 ; i ++) {
            for (int j = 0 ; j < tcp_packet_sent_time[i].length ; j ++) {
                if ( tcp_packet_sent_time[i][j] != INIT_SENT_TIME ) {
                    total_latency[i] += 10.0f - tcp_packet_sent_time[i][j];
                }
            }
        }
    }

    // TODO Update this method.
    private void increaseArraySize() {
        for (int i = 0 ; i < 2 ; i ++) {
            float[] temp = new float[tcp_packet_sent_time[0].length * 2];
            for (int j = 0 ; j < tcp_packet_sent_time[i].length ; j ++) {
                temp[j] = tcp_packet_sent_time[i][j];
            }
            tcp_packet_sent_time[i] = temp;
        }
    }

    protected void initAllCalculatingValues() {
        total_bytes = new int[] {0, 0};

        totalPacketSent = new int[] {0, 0};
        totalPacketDropped = new int[] {0, 0};
        totalPacketReceived = new int[] {0, 0};

        tcp_packet_sent_time = new float[2][ESTIMATED_TCP_PACKET_NUMBER];
        for (int i = 0 ; i < 2 ; i ++ ) {
            float[] temp = new float[ESTIMATED_TCP_PACKET_NUMBER];
            for (int j = 0 ; j < temp.length ; j ++) {
                temp[j] = INIT_SENT_TIME;
            }
            tcp_packet_sent_time[i] = temp;
        }

        total_latency = new float[] {0.0f, 0.0f};
    }

    public void start() {
        // Execute the script to generate the result files.
        for (j = 0; j < CBR_RATE.length ; j++ ) {
            String shellScript = "/course/cs4700f12/ns-allinone-2.35/bin/ns experiment2.tcl " + TCP_KIND[firstTCP] + " " + TCP_KIND[secondTCP] + " " + CBR_RATE[j];
            try {
                Runtime.getRuntime().exec(shellScript);
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        }

        // Wait a moment until everything is ready.
        try {
            Thread.sleep(3000);
        } catch (InterruptedException ex) {
            ex.printStackTrace();
        }

        // Parse the results.
        for (j = 0; j < CBR_RATE.length ; j++ ) {
            readFile("my_experimental2_output_" + TCP_KIND[firstTCP] + "_" + TCP_KIND[secondTCP] + "_" + CBR_RATE[j] + ".tr");
        }

        StringBuilder throughputStr = new StringBuilder();
        StringBuilder delayStr = new StringBuilder();
        StringBuilder dropRateStr = new StringBuilder();

        for (j = 0 ; j < CBR_RATE.length ; j ++) {
            for (int i = 0 ; i < 2 ; i ++) {
                throughputStr.append(throughputs[j][i] + " ");
                delayStr.append(delays[j][i] + " ");
                dropRateStr.append(dropRates[j][i] + " ");
            }
            throughputStr.append("\n");
            delayStr.append("\n");
            dropRateStr.append("\n");
        }

        Experiment.writeToFile("report/Report2_throughput" + "_" + TCP_KIND[firstTCP] + "_" + TCP_KIND[secondTCP], throughputStr.toString());
        Experiment.writeToFile("report/Report2_delay" + "_" + TCP_KIND[firstTCP] + "_" + TCP_KIND[secondTCP], delayStr.toString());
        Experiment.writeToFile("report/Report2_droprate" + "_" + TCP_KIND[firstTCP] + "_" + TCP_KIND[secondTCP], dropRateStr.toString());
    }

    public static void main(String[] args) {
        int[][] pairs = new int[][] {{1, 1}, {2, 1}, {3, 3}, {2, 3}};
        Experiment2 ex2;
        for (int i = 0 ; i < pairs.length ; i ++) {
            ex2 = new Experiment2(pairs[i][0], pairs[i][1]);
            ex2.start();
        }
    }
}