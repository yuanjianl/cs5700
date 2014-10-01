import java.io.*;
import java.net.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


public class WebCrawler {
    public String website;
    private Socket socket;
    private String headerCookie;

    // To prevent loop, we use a set to hold all visited pages.
    private Set<String> visitedPages = new HashSet<String>();

    // We use this deque to hold all pages need to be visited. We choose
    // Deque instead of Queue because when server shuts down the connection,
    // we can recover it and push the current page to the head of the queue.
    private Deque<String> toBeVisitedPages = new LinkedList<String>();

    // Secret flags should be unique.
    private Set<String> secretFlags = new HashSet<String>();

    // Use a PrintWriter to write to Server.
    private PrintWriter out;

    // Use a BufferedReader to get the response from Server.
    private BufferedReader in;

    private static final String COOKIE_PATTERN = "Set-Cookie: csrftoken=(\\w{32}+)";
    private static final String SESSIONID_PATTERN = "Set-Cookie: sessionid=(\\w{32}+)";
    private static final String A_HREF_PATTERN = "<a\\s.*?href=\"(/fakebook[^\"]+)\"[^>]*>(.*?)</a>";
    private static final String SECRET_FLAG_PATTERN = "<h2 class=\'secret_flag\' style=\"color:red\">FLAG: (\\w{64}+)</h2>";
    private static final String ERROR_500 = "(500 INTERNAL SERVER ERROR)";
    private static final String ERROR_301 = "(301 Moved Permanently)";
    private static final String ERROR_403 = "(403 Forbidden)";
    private static final String MESSAGE_200 = "(200 OK)";
    private static final String INVALID_USERNAME_OR_PASSWORD = "(Please enter a correct username and password. Note that both fields are case-sensitive.)";

    public WebCrawler(String website) {
        this.website = website;
        connectToServer();
    }

    /**
     * Whenever the connection is closed. Use this to reconnect with server.
     * @return True if the connection is built. False otherwise.
     */
    public boolean connectToServer() {
        try {
            this.socket = new Socket(InetAddress.getByName(website), 80);
            this.out = new PrintWriter(socket.getOutputStream());
            this.in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            return true;
        } catch (UnknownHostException e) {
            System.out.println("The host is not known!");
            System.exit(1);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return false;
    }

    /**
     * All errors in process of crawling should be handled here.
     * @param  response [description]
     * @return          [description]
     */
    public int message(String response) {
        if (response == null || response.isEmpty()) {
            // System.out.println("Response is null");
            return 800;
        } else if (response.equals("\n") || response.equals("0\n") || response.equals("null")) {
            // System.out.println("Response is null string");
            return 700;
        } else if (socket.isClosed() || socket.isInputShutdown()) {
            // System.out.println("Socket is closed.");
            return 600;
        } else if (matchPattern(response, ERROR_500).size() != 0) {
            // System.out.println("Server throws a 500 error code.");
            return 500;
        } else if (matchPattern(response, ERROR_403).size() != 0) {
            // System.out.println("Page is forbidden, discard.");
            return 403;
        } else if (matchPattern(response, ERROR_301).size() != 0) {
            // System.out.println("Page is removed permanently, fetch the new page.");
            return 301;
        } else if (matchPattern(response, MESSAGE_200).size() != 0) {
            //System.out.println("Page returns with OK messgae.");
            return 200;
        }

        return -1;
    }

    /**
     * Used a BFS to crawl the website.
     * @param path [description]
     */
    public void start(String path) {
        // Put the first page into queue.
        toBeVisitedPages.add(path);

        // If finished crawling or found all 5 flags.
        while (!toBeVisitedPages.isEmpty() && secretFlags.size() < 5) {
            String visiting = toBeVisitedPages.poll();
            request(website, visiting, headerCookie, null);
            String response = read();
            // System.out.println("The page is: " + visiting + "\n" + response + "\n");

            int message = message(response);
            // If server throws a 500 error, reconnect to server and retry the current url.

            if (message >= 500 || message < 0) {
                connectToServer();

                // If we cannot recover the socket, close the program.
                if (socket.isClosed()) {
                    System.out.println("Encounting an unrecoverble error, exiting.");
                    System.exit(1);
                }
                // Put the current url to the head of the list.
                toBeVisitedPages.addFirst(visiting);
                continue;
            } else if (message == 403) {
                // If server returns reponse with error 403, just abandon the URL. Before that, we want to put it in the visited pages so that we won't visit it again.
                visitedPages.add(visiting);
                continue;
            }

            // Sucessfully visited the page, add to visitedPages.
            visitedPages.add(visiting);

            // If found the flags, put in flags set.
            List<String> flags = matchPattern(response, SECRET_FLAG_PATTERN);
            for (String flag : flags) {
                secretFlags.add(flag);
            }

            // Put newly found pages into queue.
            List<String> hrefs = matchPattern(response, A_HREF_PATTERN);
            for (String href : hrefs) {
                if (isOuterLink(href)){
                    continue;
                }
                if (!visitedPages.contains(href)) {
                    toBeVisitedPages.add(href);
                    // System.out.println("To be visitied: " + href);
                }
            }
            // System.out.println("To be visited queue size is: " + toBeVisitedPages.size() + ". And secret flag is: " + secretFlags.size());

        }
        // When finished, print out all 5 flags.
        for (String flag : secretFlags) {
            System.out.println(flag);
        }
    }

    /**
     * The outerlink should have "http" or "https" in the href.
     * @param  href [description]
     * @return      [description]
     */
    private boolean isOuterLink(String href){
        href = href.toLowerCase();
        return href.contains("http");
    }

    public String getCookie() {
        return headerCookie;
    }

    /**
     * The request is an abstract of Post and Get method. If data
     * is not null, use Post method, otherwise the Get method.
     * @param host The host of the website
     * @param path The path of the request
     * @param data the request body
     */
    public void request(String host, String path, String cookie, String data) {
        // Use the Get method if data is null or empty.
        if (data == null || data.equals("")) {
            out.println("GET " + path + " HTTP/1.1");
            out.println("Host: " + host);
            out.println("Connection: keep-alive");
            if (cookie != null) {
                out.println("Cookie: " + cookie);
            }
            out.println("User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36");
            out.println("");
            out.flush();
        } else {
            out.println("POST " + path + " HTTP/1.1");
            out.println("Host: " + host);
            out.println("Connection: keep-alive");
            out.println("Cookie: " + cookie);
            out.println("User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36");
            out.println("Content-Length: " + data.length());
            out.println("Content-Type: application/x-www-form-urlencoded; charset=utf-8");
            out.println("");
            out.println(data);
            out.flush();
        }

    }

    public void login(String path, String username, String password) {
        // Initial GET request to /accounts/login/.
        request(website, path, null, null);
        String response = read();
        // System.out.println(response);

        // POST request to /accounts/login/ to log in for cookie and sessionid.
        String cookie = matchPattern(response, COOKIE_PATTERN).get(0);
        String sessionid = matchPattern(response, SESSIONID_PATTERN).get(0);
        String data = "username=" + username + "&password=" + password + "&csrfmiddlewaretoken=" + cookie;
        String headerCookie = "csrftoken=" + cookie + "; sessionid=" + sessionid;
        request(website, path, headerCookie, data);
        response = read();
        // System.out.println("response22: "+response);

        if (matchPattern(response, INVALID_USERNAME_OR_PASSWORD).size() != 0){
            System.err.println("Wrong username and/or passwords. Terminating program.");
            System.exit(1);
        }

        // The server will return a new session_id if login successful.
        List<String> matchResult = matchPattern(response, SESSIONID_PATTERN);
        // Try to reconnect with the server if login fails for the first time;
        if (matchResult.size() == 0){
            request(website, path, headerCookie, data);
            response = read();
            matchResult = matchPattern(response, SESSIONID_PATTERN);
        } 
        if (matchResult.size() == 0){
            System.err.println("Login fails by the server. Terminating.");
            System.exit(1);
        } 
        sessionid = matchResult.get(0);

        // This header cookie should be used
        this.headerCookie = "csrftoken=" + cookie + "; sessionid=" + sessionid;
    }

    public List<String> matchPattern(String response, String pattern) {
        Pattern r = Pattern.compile(pattern);
        Matcher m = r.matcher(response);
        List<String> results = new ArrayList<String>();
        while (m.find()) {
            String t = m.group(1);
            results.add(t);
        }
        return results;
    }

    public String read() {
        String t;
        StringBuilder sb = new StringBuilder();
        try {
            // The server would hang 5 seconds before closing the socket. To skip this, we
            // add a in.ready() to check if server has more things to send.
            while (true) {
                t = in.readLine();
                // System.out.println(t);
                sb.append(t);
                if (!in.ready())
                    break;
            }
        } catch (IOException e) {
            System.out.println(e);
            System.out.println("There is an error in reading the response from server.");
        }
        return sb.toString();
    }

    public void finish() throws IOException {
        in.close();
        out.close();
        socket.close();
    }

    public static void main(String[] args) throws IOException {
        if (args.length != 4) {
            System.err.println("Usage: java WebCrawler <host name> <path> <username> <passsword>");
            System.exit(1);
        }
        String website = args[0];
        String path = args[1];
        String username = args[2];
        String password = args[3];


        try {
            WebCrawler crawler = new WebCrawler(website);

            crawler.login("/accounts/login/", username, password);

            crawler.start(path);

            crawler.finish();
        } catch (NullPointerException ex) {
            System.err.println("Null Pointer Exception. Terminating");
            ex.printStackTrace();
        }
    }


}
