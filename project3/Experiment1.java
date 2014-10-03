public class Experiment1 extends Experiment {

    private String[] TCP_KIND = {"Tahoe", "Reno", "NewReno", "Vegas"};
    private int[] CBR_RATE = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    protected void getFeed(String line){
        System.out.println(line);
    }

    protected String result(){
        return null;
    }

    public void start(){
        for (int i = 0 ; i < TCP_KIND.length ; i ++){
            for (int j = 0; j < CBR_RATE.length ; j++ ) {
                String shellScript = "/course/cs4700f12/ns-allinone-2.35/bin/ns experiment1 " + TCP_KIND[i] + " " + CBR_RATE[j];
                Runtime.getRuntime().exec(shellScript);
                readFile("my_experimental1_output_" + TCP_KIND[i] + "_" + CBR_RATE[j] + ".tr");
                break;
            }
        }
    }

    public static void main(String[] args) {
        Experiment1 ex1 = new Experiment1();
        ex1.start();
    }
}