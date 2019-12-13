package fr.ceri.tools;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

public class TweetDataExtractor
{
    private static URL indexUrl;
    private List<String> extractedData;

    public TweetDataExtractor() throws MalformedURLException
    {
        indexUrl = new URL("http://localhost:9200/tweets");
        extractedData = new ArrayList<>();
    }

    public List<String> fromIndexGet(String field) throws IOException
    {
        HttpURLConnection con = (HttpURLConnection) indexUrl.openConnection();
        con.setRequestMethod("POST");

        return null;
    }
}
