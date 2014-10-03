import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileNotFoundException;
import java.io.IOException;

public abstract class Experiment {

    public void readFile(String filename){
        try {
            BufferedReader br = new BufferedReader(new FileReader(filename));
            String line = br.readLine();

            while (line != null) {
                getFeed(line);
                line = br.readLine();
            }
            br.close();
            System.out.println(result());
        } catch (FileNotFoundException ex) {
            System.err.println("File not found, terminating.");
            System.exit(1);
        } catch (IOException ex){
            System.err.println("IOException, terminating");
            System.exit(1);
        }
    }

    abstract void getFeed(String line);

    abstract String result();
}