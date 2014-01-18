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

    public Client(String host, int port, boolean isSSL){
        try {
            if (isSSL) {
                    X509TrustManager xtm = new Java2000TrustManager();
                    TrustManager mytm[] = { xtm };
        
                    SSLContext ctx = SSLContext.getInstance("SSL");
                    ctx.init(null, mytm, null);
                    SSLSocketFactory factory = ctx.getSocketFactory();
        
                    // SSLSocketFactory factory=(SSLSocketFactory) SSLSocketFactory.getDefault();
                    this.serverSocket = (SSLSocket) factory.createSocket(host, port);
            } else {
                this.serverSocket = new Socket(host, port);
            }
            this.out = new PrintWriter(serverSocket.getOutputStream(), true);
            this.in = new BufferedReader(new InputStreamReader(serverSocket.getInputStream()));
        } catch (NoSuchAlgorithmException e){
            System.out.println("SSL algorithm is not found!.");
        } catch (KeyManagementException e) {

        } catch (IOException e){

        }
    }

    /**
     * This method returns the solution in STATUS message.
     */
    private static String getSolution(String response){
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
    private static long getResult(int firstOperand, String operator, int secondOperand){
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

    public static void main(String args[]) throws IOException{
        if (args.length != 4){
            System.err.println("Usage: java Client <host name> <port number> <nuID> <useSSL>");
            System.exit(1);
        }
        String host = args[0];
        int port = Integer.parseInt(args[1]);
        String nuID = args[2];
        boolean isSSL = Boolean.parseBoolean(args[3]);

        Client client = new Client(host, port, isSSL);

        out.println("cs5700spring2014 HELLO " + nuID);
        String response;
        while (true){
            response = in.readLine();
            if (response == null || !response.contains("STATUS"))
                break;
            else 
                out.println("cs5700spring2014 " + getSolution(response));
        }
        System.out.println("Final response with secret flag: " + response);
        // When done, just close the connection and exit
        out.close();
        in.close();
        serverSocket.close();
    }
}

class Java2000TrustManager implements X509TrustManager {
    Java2000TrustManager() {

    }

    public void checkClientTrusted(X509Certificate chain[], String authType) throws CertificateException {
    }

    public void checkServerTrusted(X509Certificate chain[], String authType) throws CertificateException {
    }

    public X509Certificate[] getAcceptedIssuers() {
        return null;
    }
}