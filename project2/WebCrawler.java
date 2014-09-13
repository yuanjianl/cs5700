import java.io.*;
import java.net.*;
import java.util.*;


public class WebCrawler {
    public String website;
    private Socket socket;
    private Set<String> visitedPages = new HashSet<String>();
    // private Queue<String> toBeVisitedPages = new Queue<String>();
    // Use a PrintWriter to write to Server.
    public static PrintWriter out;
    // Use a BufferedReader to get the response from Server.
    public static BufferedReader in;

    public WebCrawler(String website) {
        this.website = website;
        try {
            this.socket = new Socket(InetAddress.getByName(website), 80);
            this.out = new PrintWriter(socket.getOutputStream());
            this.in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        } catch (UnknownHostException e){
            System.out.println("The host is not known!");
        } catch (IOException e){
            e.printStackTrace();
        }
    }

    public void start(){
        // String responseHTML = goToRootPage();
        
        // toBeVisitedPages.add(getLinks(responseHTML));
        // while (toBeVisitedPages.size()){
        //     String nextPage = toBeVisitedPages.pop();
        //     if (!visitedPages.contains(nextPage)){
        //         responseHTML = visitPage(nextPage);
        //         toBeVisitedPages.add(getLinks(responseHTML));
        //     }
        // }
    }

    public static void main(String[] args)  throws IOException{
        if (args.length != 4) {
            System.err.println("Usage: java WebCrawler <host name> <path> <username> <passsword>");
            System.exit(1);
        }
        String website = args[0];
        String path = args[1];
        String username = args[2];
        String password = args[3];

        

        WebCrawler crawler = new WebCrawler(website);
        out.println("POST " + "/accounts/login/" + " HTTP/1.1");
        out.println("Host: " + website + "");
        out.println("Cookie: csrftoken=ef5701548275a17c885b1ed15c27dbac; sessionid=c1e3c1d964cc2ee0b14b5b59ab9574c9");
        out.println("Content-Length: 99");
        // out.println("Content-type: application/x-www-form-urlencoded; charset=utf-8");
        out.println("");
        out.println("csrfmiddlewaretoken=ef5701548275a17c885b1ed15c27dbac&username=zmi&password=m6066022&next=/fakebook/");

        // out.println("<html><form method=\"post\" action=\".\">");
        // out.println("<input id=\"id_username\" value=\"zmi\" />");
        // out.println("<input id=\"id_password\" value=\"m6066022\" />");
        // out.println("<input type=\"submit\" value=\"Log in\" />");
        // out.println("<input type=\"hidden\" name=\"next\" value=\"/fakebook/\" />");
        // out.println("</form></html>");
        out.flush();

        String t;
        String sessionID = "";
        while ((t = in.readLine()) != null){
            System.out.println(t);
            if (t.startsWith("Set-Cookie: ")){
                int index = t.indexOf("sessionid=");
                sessionID = t.substring(index + 10, index + 42);
                System.out.println(sessionID);
                break;
            }
        }

        System.out.println("Get request!!");
        out.println("GET " + "/fakebook/" + " HTTP/1.1");
        out.println("Host: " + website + "");
        // out.println("Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8");
        // out.println("Connection: keep-alive");
        out.println("Cookie: csrftoken=ef5701548275a17c885b1ed15c27dbac; sessionid=" + sessionID);
        // out.println("Content-Type: application/x-www-form-urlencoded");
        // out.println("Content-Length: 89");
        // out.println("Content-type: application/x-www-form-urlencoded; charset=utf-8");
        out.println("");
        out.flush();

        while ((t = in.readLine()) != null)
            System.out.println(t);

        in.close();
        out.close();

    }


}