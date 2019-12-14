package fr.ceri.entities;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.tartarus.snowball.SnowballStemmer;
import org.tartarus.snowball.ext.frenchStemmer;

import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class WordProcessor
{
    private Map<String, String> wordList;
    private String targetDataFile;
    private String inputFile;

    public WordProcessor()
    {
        wordList = new HashMap<>();
        inputFile = "src/fr/ceri/data/external/FEEL.csv";
        targetDataFile = "src/fr/ceri/data/annotated/words.json";
    }

    public Map<String, String> getWordList()
    {
        return wordList;
    }

    public String getTargetDataFile()
    {
        return targetDataFile;
    }

    public void convertToWordMapAndStem() throws IOException
    {
        Reader input = Files.newBufferedReader(Paths.get(inputFile));
        CSVFormat format = CSVFormat.DEFAULT.withDelimiter(';');
        CSVParser parser = new CSVParser(input, format);

        List<CSVRecord> records = parser.getRecords();

        for (CSVRecord record : records)
        {
            // Stemming
            SnowballStemmer stemmer = new frenchStemmer();
            stemmer.setCurrent(record.get(1));
            stemmer.stem();
            wordList.put(stemmer.getCurrent(), record.get(2));
        }
    }
}
