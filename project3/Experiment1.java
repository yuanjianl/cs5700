import java.io.IOException;
import java.lang.InterruptedException;

public class Experiment1 extends Experiment {

    private String[] TCP_KIND = {"Tahoe", "Reno", "NewReno", "Vegas"};
    private int[] CBR_RATE = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    // Variables for recording.

    private int i = TCP_KIND.length;
    private int j = CBR_RATE.length;
    private float[][] throughputs = new float[j][i];
    private float[][] delays = new float[j][i];
    private float[][] dropRates = new float[j][i];

    // Variables for calculating.

    // For throughput, I used the packet received at the end node to calculate.
    private int total_bytes;

    // For drop rate, I simply use the largest global packet number as the
    // total number of sent packet. The number of dropped packet are calculated
    // as number of d.
    private int totalPacketSent;
    private int totalPacketDropped;
    private int totalPacketReceived;

    // For latency, I used a float[] to hold all sent time. The init value is -1.0f;
    private float[] tcp_packet_sent_time;
    private float total_latency;

    public Experiment1() {
        initAllCalculatingValues();
    }

    protected void getFeed(String line) {
        String[] trace = line.split(" ");

        String messageType = trace[MESSAGE_TYPE];
        if ( messageType.equals(DROPPED) && trace[PACKET_TYPE].equals(TCP)) {
            totalPacketDropped += 1;
        }
        // If it's a DEQUEUED message at node 0, it is a tcp out packet.
        else if ( messageType.equals(DEQUEUED) && trace[SENDER].equals("0") ) {
            totalPacketSent += 1;

            float time = Float.parseFloat(trace[TIME]);
            int seqNum = Integer.parseInt(trace[trace.length - 2]);

            // If the current float[] is not big enough, double it.
            if (seqNum >= tcp_packet_sent_time.length ) {
                increaseArraySize();
            }

            if (tcp_packet_sent_time[seqNum] == INIT_SENT_TIME) {
                tcp_packet_sent_time[seqNum] = time;
            }
        } else if ( messageType.equals(RECEIVED) ) {
            if ( trace[RECEIVER].equals("0") && trace[PACKET_TYPE].equals(ACK) ) {
                float time = Float.parseFloat(trace[TIME]);
                int seqNum = Integer.parseInt(trace[trace.length - 2]);

                // If the sent time is -1.0, there is an error. Ignore it.
                if (tcp_packet_sent_time[seqNum] != INIT_SENT_TIME) {
                    total_latency += time - tcp_packet_sent_time[seqNum];
                    totalPacketReceived += 1;
                    total_bytes += 1040;
                    tcp_packet_sent_time[seqNum] = INIT_SENT_TIME;
                }
            }
        }
    }

    protected void result() {
        getLostPackets();

        float throuput = 8.0f * (total_bytes) / (10 * 1000 * 1000);
        float delay = 1000.0f * total_latency / totalPacketReceived;
        float dropRate = 100.0f * (totalPacketSent - totalPacketReceived) / totalPacketSent;

        throughputs[j][i] = throuput;
        delays[j][i] = delay;
        dropRates[j][i] = dropRate;

        initAllCalculatingValues();
    }

    private int getLostPackets() {
        int result = 0;
        for (int i = 0 ; i < tcp_packet_sent_time.length ; i ++) {
            if ( tcp_packet_sent_time[i] != INIT_SENT_TIME ) {
                total_latency += 10.0f - tcp_packet_sent_time[i];
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
        total_bytes = 0;

        totalPacketSent = 0;
        totalPacketDropped = 0;
        totalPacketReceived = 0;

        tcp_packet_sent_time = new float[ESTIMATED_TCP_PACKET_NUMBER];
        for (int i = 0 ; i < tcp_packet_sent_time.length ; i ++) {
            tcp_packet_sent_time[i] = INIT_SENT_TIME;
        }

        total_latency = 0.0f;
    }

    public void start() {
        // Execute the script to generate the result files.
        for (i = 0 ; i < TCP_KIND.length ; i ++) {
            for (j = 0; j < CBR_RATE.length ; j++ ) {
                String shellScript = "/course/cs4700f12/ns-allinone-2.35/bin/ns experiment1.tcl " + TCP_KIND[i] + " " + CBR_RATE[j];
                try {
                    Runtime.getRuntime().exec(shellScript);
                } catch (IOException ex) {
                    ex.printStackTrace();
                }
            }
        }

        // Wait a moment until everything is ready.
        try {
            Thread.sleep(5000);
        } catch (InterruptedException ex) {
            ex.printStackTrace();
        }

        // Parse the results.
        for (i = 0 ; i < TCP_KIND.length ; i ++) {
            for (j = 0; j < CBR_RATE.length ; j++ ) {
                readFile("my_experimental1_output_" + TCP_KIND[i] + "_" + CBR_RATE[j] + ".tr");
            }
        }

        StringBuilder throughputStr = new StringBuilder();
        StringBuilder delayStr = new StringBuilder();
        StringBuilder dropRateStr = new StringBuilder();

        for (j = 0 ; j < CBR_RATE.length ; j ++) {
            for (i = 0 ; i < TCP_KIND.length ; i ++) {
                throughputStr.append(throughputs[j][i] + " ");
                delayStr.append(delays[j][i] + " ");
                dropRateStr.append(dropRates[j][i] + " ");
            }
            throughputStr.append("\n");
            delayStr.append("\n");
            dropRateStr.append("\n");
        }

        Experiment.writeToFile("report/Report1_throughput", throughputStr.toString());
        Experiment.writeToFile("report/Report1_delay", delayStr.toString());
        Experiment.writeToFile("report/Report1_droprate", dropRateStr.toString());
    }

    public static void main(String[] args) {
        Experiment1 ex1 = new Experiment1();
        ex1.start();
    }
}