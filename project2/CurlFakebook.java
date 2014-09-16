public class CurlFakebook extends WebCrawler{
    private final static String website = "cs5700f14.ccs.neu.edu";

    public CurlFakebook(String path, String username, String password){
        super(website);

        login("/accounts/login/", username, password);

        String cookie = getCookie();

        request(website, path, cookie, null);
        System.out.println(read());
    }
    

    public static void main(String[] args){
        String path = args[0];
        String username = args[1];
        String password = args[2];

        CurlFakebook instance1 = new CurlFakebook(path, username, password);
    }
}
