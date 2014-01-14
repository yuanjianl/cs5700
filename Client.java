import java.net.*;
import java.io.*;
public class Client {

    public static void main(String args[]) throws IOException {
        if (args.length != 3){
            System.err.println("Usage: java Client <host name> <port number> <nuID>");
            System.exit(1);
        }
        String host = args[0];
        int port = Integer.parseInt(args[1]);
        String nuID = args[2];

        // Create the Socket with server.
        Socket serverSocket = new Socket(host, port);
        // Create a PrintWriter to write to Server.
        PrintWriter out = new PrintWriter(serverSocket.getOutputStream(), true);
        // Create a BufferedReader to get the response from Server.
        BufferedReader in = new BufferedReader(new InputStreamReader(serverSocket.getInputStream()));
        out.println("cs5700spring2014 HELLO " + nuID);
        String response;
        while (true){
            response = in.readLine();
//            System.out.println(response);
            if (response == null || !response.contains("STATUS"))
                break;
            else 
                out.println(getSolution(response));
        }
        System.out.println("Final response with secret flag: " + response);
        // When done, just close the connection and exit
        out.close();
        in.close();
        serverSocket.close();
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
//        System.out.println(result);
        return "cs5700spring2014 " + String.valueOf(result);
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
}