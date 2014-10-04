import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileNotFoundException;
import java.io.IOException;

public abstract class Experiment {

    final static int ESTIMATED_TCP_PACKET_NUMBER = 10000;
    final static float INIT_SENT_TIME = -1.0f;

    // Message type.
    final static String RECEIVED = "r";
    final static String DROPPED = "d";
    final static String DEQUEUED = "-";

    // Packet type
    final static String CBR = "cbr";
    final static String TCP = "tcp";

    final static int MESSAGE_TYPE = 0;
    final static int TIME = 1;
    final static int SENDER = 2;
    final static int RECEIVER = 3;
    final static int PACKET_TYPE = 4;
    final static int PACKET_SIZE = 5;

    void readFile(String filename){
        try {
            BufferedReader br = new BufferedReader(new FileReader(filename));
            String line = br.readLine();

            while (line != null) {
                getFeed(line);
                line = br.readLine();
            }
            br.close();
            System.out.println(result());
        } catch (FileNotFoundException ex) {
            // System.err.println("File not found, terminating.");
            // System.exit(1);
            readFile(filename);
        } catch (IOException ex){
            System.err.println("IOException, terminating");
            System.exit(1);
        }
    }

    abstract void getFeed(String line);

    abstract String result();
}