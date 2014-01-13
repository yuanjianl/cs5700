import java.net.*;
import java.io.*;
public class Client {
    public static void main(String args[]) throws IOException {
        Socket s1 = new Socket("cs5700.ccs.neu.edu",27993);
        OutputStream s1Out = s1.getOutputStream();
        DataOutputStream dos = new DataOutputStream (s1Out);
		dos.writeChars("cs5700spring2014 HELLO 001101264\n");
        // Get an input file handle from the socket and read the input
        InputStream s1In = s1.getInputStream();
        // System.out.println("Scoekt Address: " + s1.getRemoteSocketAddress());
        // System.out.println("Socket is connected: " + s1.isConnected());
        // System.out.println("Socket available: " + s1In.available());
        BufferedReader br =
                new BufferedReader(
                    new InputStreamReader(s1.getInputStream()));
        StringBuilder sb = new StringBuilder();
		String line;
		while ((line = br.readLine()) != null) {
				sb.append(line);
		}

        System.out.println(sb);
        // When done, just close the connection and exit
        br.close();
        s1In.close();
        s1.close();
   }
}