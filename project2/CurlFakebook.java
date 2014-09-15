public class CurlFakebook extends WebCrawler{
    private final static String website = "cs5700f14.ccs.neu.edu";

    public CurlFakebook(String path){
        super(website);

        login("/accounts/login/", "forevermzm", "m6066022");

        String cookie = getCookie();

        request(website, path, cookie, null);
        System.out.println(read());
    }
    

    public static void main(String[] args){
        String path = args[0];

        CurlFakebook instance1 = new CurlFakebook(path);
    }
}