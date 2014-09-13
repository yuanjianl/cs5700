import java.io.*;
import java.net.*;
import java.util.*;
import java.util.regex.Pattern;

public class CS5700WebCrawler extends WebCrawler{
    private static final int FLAG_NUMBER = 5;
    private Set<String> secretFlags = new HashSet<String>();

    public CS5700WebCrawler(String website){
        super(website);
    }

    public String login(String username, String password){
        out.println("POST " + "/accounts/login/" + " HTTP/1.1");
        out.println("Host: " + website + "");
        out.println("Cookie: csrftoken=ef5701548275a17c885b1ed15c27dbac; sessionid=c1e3c1d964cc2ee0b14b5b59ab9574c9");
        // out.println("Content-Length: " + content.length());
        // out.println("Content-type: application/x-www-form-urlencoded; charset=utf-8");
        out.println("");
        out.flush();
        Pattern patten = Pattern.compile("Set Cookie: ");
        String content = "csrfmiddlewaretoken=ef5701548275a17c885b1ed15c27dbac&username=" + username + "&password=" + password + "&next=/fakebook/";
        out.println("POST " + "/accounts/login/" + " HTTP/1.1");
        out.println("Host: " + website + "");
        out.println("Cookie: csrftoken=ef5701548275a17c885b1ed15c27dbac; sessionid=c1e3c1d964cc2ee0b14b5b59ab9574c9");
        out.println("Content-Length: " + content.length());
        // out.println("Content-type: application/x-www-form-urlencoded; charset=utf-8");
        out.println("");
        out.println(content);
        out.flush();
        return null;
    }

    public void start(){

        // String responseHTML = goToRootPage();
        
        // toBeVisitedPages.add(getLinks(responseHTML));
        // while (toBeVisitedPages.size() && secretFlags.size() < FLAG_NUMBER){
        //     String nextPage = toBeVisitedPages.pop();
        //     if (!visitedPages.contains(nextPage)){
        //         responseHTML = visitPage(nextPage);
        //         String flag = findFlag(responseHTML);
        //         if (flag)
        //             secretFlags.add(flag);
        //         toBeVisitedPages.add(getLinks(responseHTML));
        //     }
        // }
    }

    public String findFlag(String page){
        return null;
    }

    public void read() throws IOException{
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

    public static void main(String[] args) throws IOException{
        if (args.length != 4) {
            System.err.println("Usage: java CS5700WebCrawler <host name> <path> <username> <passsword>");
            System.exit(1);
        }
        String website = args[0];
        String path = args[1];
        String username = args[2];
        String password = args[3];

        CS5700WebCrawler crawler = new CS5700WebCrawler(website);
        crawler.login(username, password);

        crawler.read();
    }
}