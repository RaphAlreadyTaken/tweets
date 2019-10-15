package fr.ceri;

import java.io.*;
import java.util.HashMap;
import java.util.Map;

public class LexiqueCreator
{
    private static String lexiqueFileName = "lexique.txt";

    private HashMap<String, Integer> lexique;
    private int lexiqueSize;

    public LexiqueCreator()
    {
        lexique = new HashMap<>();
        lexiqueSize = 0;
    }

    public HashMap<String, Integer> loadLexiqueFromFile() throws IOException
    {
        FileInputStream fis = new FileInputStream(lexiqueFileName);
        BufferedReader reader = new BufferedReader(new InputStreamReader(fis));

        String currentStr;

        while ((currentStr = reader.readLine()) != null)
        {
            String[] strs = currentStr.split("\\t");
            this.lexique.put(strs[0], Integer.valueOf(strs[1]));
        }

        this.lexiqueSize = this.lexique.size();

        return this.lexique;
    }

    public void writeLexiqueToFile() throws IOException
    {
        this.lexique.put("Toto", 0);
        this.lexique.put("Toto2", 6846546);
        this.lexique.put("Toto3", -8);

        BufferedWriter writer = new BufferedWriter(new FileWriter(lexiqueFileName, false));

        for (Map.Entry entry : this.lexique.entrySet())
        {
            writer.write(entry.getKey() + "\t" + entry.getValue());
            writer.newLine();
        }

        writer.close();
    }

    public void transformTweets(File dataFile) throws Exception
    {
        this.loadLexiqueFromFile();

        FileInputStream fis = new FileInputStream(dataFile);
        BufferedReader reader = new BufferedReader(new InputStreamReader(fis));
        BufferedWriter writer = new BufferedWriter(new FileWriter("toto.svm", false));

        String currentRow;

        while ((currentRow = reader.readLine()) != null)
        {
            if (!currentRow.isEmpty() && currentRow.charAt(0) != '/')
            {
                String[] row = currentRow.split("\\t");  //[tweet],[opinion]

                ///Opinion
                int label = this.opinionToInt(row[2]);  //Label (-1..3)

                if (label == -1)
                {
                    throw new Exception("Invalid opinion value");
                }

                ///Tweet
//                String[] tweetWords = row[1].split("[^\\p{L}\\p{N}]");    //[mot1],[mot2],[mot3], ...
                String[] tweetWords = row[1].split(" ");    //[mot1],[mot2],[mot3], ...

                StringBuilder valueToWrite = new StringBuilder();
                valueToWrite.append(label).append(" ");

                for (String str : tweetWords)
                {
                    ///Gestion lexique
                    if (!this.lexique.containsKey(str))  //pas présent, on rajoute
                    {
                        this.lexiqueSize++;
                        this.lexique.put(str, this.lexiqueSize);
                    }

                    ///Valeur de sortie
                    int cpt_word = 0;

                    for (String str2 : tweetWords)  //boucle optimisée pour compter la fréquence du mot
                    {
                        if (str2.equals(str))
                        {
                            cpt_word++;
                        }
                    }

                    valueToWrite.append(this.lexique.get(str)).append(":").append(cpt_word).append(" ");
                }

//                valueToWrite.append(" \n"); //fin du tweet
                writer.write(valueToWrite.toString());
                writer.newLine();
            }
        }

        this.writeLexiqueToFile();
    }

    public int opinionToInt(String opinion)
    {
        int result;

        switch (opinion)
        {
            case "objective":
                result = 0;
                break;
            case "positive":
                result = 1;
                break;
            case "negative":
                result = 2;
                break;
            case "mixed":
                result = 3;
                break;
            default:
                result = -1;
                break;
        }

        return result;
    }
}
