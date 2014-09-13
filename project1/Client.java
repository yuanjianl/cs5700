import java.net.*;
import java.io.*;
import javax.net.ssl.*;
import java.security.cert.X509Certificate;
import java.security.cert.CertificateException;
import java.security.*;

public class Client {

    private static Socket serverSocket;
    // Use a PrintWriter to write to Server.
    private static PrintWriter out;
    // Use a BufferedReader to get the response from Server.
    private static BufferedReader in;

    private static String MESSAGE_PREFIX = "cs5700fall2014";

    public Client(String host, int port, boolean isSSL) {
        try {
            if (isSSL) {
                System.setProperty("javax.net.ssl.trustStore", "jssecacerts");
                SSLSocketFactory factory = (SSLSocketFactory) SSLSocketFactory.getDefault();
                SSLSocket socket = (SSLSocket) factory.createSocket(host, port);
                this.serverSocket = (SSLSocket) socket;
            } else {
                this.serverSocket = new Socket(host, port);
            }
            this.out = new PrintWriter(this.serverSocket.getOutputStream(), true);
            this.in = new BufferedReader(new InputStreamReader(this.serverSocket.getInputStream()));
        } catch (IOException e) {
            System.out.println(e);
            System.out.println("The host cannot be reached");
        }
    }

    /**
     * This method returns the solution in STATUS message.
     */
    private static String getSolution(String response) {
        String[] messages = response.split(" ");
        int numberOfMessages = messages.length;
        int firstOperand = Integer.parseInt(messages[numberOfMessages - 3]);
        int secondOperand = Integer.parseInt(messages[numberOfMessages - 1]);
        String operator = messages[numberOfMessages - 2];
        long result = getResult(firstOperand, operator, secondOperand);
        return String.valueOf(result);
    }

    /**
     * Given two operands and the operator, this method will return the math result.
     */
    private static long getResult(int firstOperand, String operator, int secondOperand) {
        long result = 0;
        if (operator.equals("+")) {
            result = firstOperand + secondOperand;
        } else if (operator.equals("-")) {
            result = firstOperand - secondOperand;
        } else if (operator.equals("*")) {
            result = firstOperand * secondOperand;
        } else if (operator.equals("/")) {
            result = firstOperand / secondOperand;
        }
        return result;
    }

    public static void main(String args[]) throws IOException {
        if (args.length != 4) {
            System.err.println("Usage: java Client <host name> <port number> <nuID> <useSSL>");
            System.exit(1);
        }
        String host = args[0];
        int port = Integer.parseInt(args[1]);
        String nuID = args[2];
        boolean isSSL = Boolean.parseBoolean(args[3]);

        Client client = new Client(host, port, isSSL);
        
        if (out == null) {
            System.out.println("The socket is not properly set.");
            System.exit(1);
        }
        out.println(MESSAGE_PREFIX + " HELLO " + nuID);
        String response;
        while (true) {
            response = in.readLine();
            if (response == null || !response.contains("STATUS"))
                break;
            else {
                System.out.println(getSolution(response));
            }
        }
        System.out.println(response.split(" ")[1]);
        // When done, just close the connection and exit
        out.close();
        in.close();
        serverSocket.close();
    }
}