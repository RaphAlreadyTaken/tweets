package fr.ceri.entities;

import java.util.HashMap;
import java.util.Map;

public class WordProcessor
{
    private Map<String, String> wordList;
    private String targetDataFile;

    public WordProcessor()
    {
        wordList = new HashMap<>();
        targetDataFile = "src/fr/ceri/data/hashtags.json";;
    }
}
