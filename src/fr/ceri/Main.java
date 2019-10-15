package fr.ceri;

import java.io.*;
import java.util.Arrays;

public class Main
{
    public static void main(String[] args) throws FileNotFoundException
    {
        try
        {
            System.out.println("Tweets");

            LexiqueCreator lexLuthor = new LexiqueCreator();
            lexLuthor.writeLexiqueToFile();
            lexLuthor.transformTweets(new File("src/fr/ceri/data/task1-train.csv"));
        }
        catch (Exception ex)
        {
            System.out.println("Exception caught:" + ex.getMessage());
            System.out.println("Stack trace:" + Arrays.toString(ex.getStackTrace()));
        }
    }
}
