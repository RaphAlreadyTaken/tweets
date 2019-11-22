package fr.ceri;
import org.json.JSONObject;
import org.json.XML;

import java.io.*;
import java.util.Arrays;

public class Main
{

    public static void main(String[] args) throws IOException
    {
        String testFile = new File("src/fr/ceri/data/unlabeled.xml").toString();
        System.out.println(testFile);

        FileInputStream fis = new FileInputStream("src/fr/ceri/data/unlabeled.xml");
        BufferedReader reader = new BufferedReader(new InputStreamReader(fis));

        JSONObject myJsonObj = XML.toJSONObject(reader, true);
//        System.out.println();

        BufferedWriter writer = new BufferedWriter(new FileWriter("src/fr/ceri/data/unlabeled_test_string.json"));
        writer.write(myJsonObj.toString(4));
        writer.close();

//        try
//        {
//            System.out.println("Tweets");
//
//            LexiqueCreator lexLuthor = new LexiqueCreator();
//            lexLuthor.writeLexiqueToFile();
//            lexLuthor.transformTweets(new File("src/fr/ceri/data/task1-train.csv"));
//        }
//        catch (Exception ex)
//        {
//            System.out.println("Exception caught:" + ex.getMessage());
//            System.out.println("Stack trace:" + Arrays.toString(ex.getStackTrace()));
//        }
    }
}
