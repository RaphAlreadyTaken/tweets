package fr.ceri.entities;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.elasticsearch.search.SearchHit;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class HashtagProcessor
{
    private Map<String, Integer> hashMap;
    private String targetDataFile;
    private ObjectMapper mapper;

    public HashtagProcessor()
    {
        hashMap = new HashMap<>();
        targetDataFile = "../common/data/raw/hashtags.json";
        mapper = new ObjectMapper();
    }

    public Map<String, Integer> getHashMap()
    {
        return hashMap;
    }

    public String getTargetDataFile()
    {
        return targetDataFile;
    }

    public void convertToHashtagMap(List<SearchHit> hits, String field)
    {
        int i = 0;

        for (SearchHit hit : hits)
        {
            Object hashtags = hit.getSourceAsMap().get(field);

            if (hashtags != null)
            {
                JsonNode[] nodes = mapper.convertValue(hashtags, JsonNode[].class);

                for (JsonNode node : nodes)
                {
                    hashMap.put(node.get("text").asText(), i);
                    i++;
                }
            }
        }
    }

    public void displayHashtagMap()
    {
        System.out.println("-- Displaying " + hashMap.size() + " hashtags --");

        for (Map.Entry<String, Integer> entry : hashMap.entrySet())
        {
            System.out.println(entry.getKey() + " → " + entry.getValue());
        }
    }
}
