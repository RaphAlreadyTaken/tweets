package fr.ceri.entities;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.elasticsearch.search.SearchHit;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class HashtagProcessor
{
    private Map<String, Integer> hashList;

    public HashtagProcessor()
    {
        hashList = new HashMap<>();
    }

    public void convertToHashtagMap(List<SearchHit> hits, String field)
    {
        for (SearchHit hit : hits)
        {
            Object hashtags = hit.getSourceAsMap().get(field);

            if (hashtags != null)
            {
                ObjectMapper mapper = new ObjectMapper();
                JsonNode[] nodes = mapper.convertValue(hashtags, JsonNode[].class);

                for (JsonNode node : nodes)
                {
                    hashList.put(node.get("text").asText(), 0);
                }
            }
        }
    }

    public void displayHashtagMap()
    {
        System.out.println("-- Displaying " + hashList.size() + " hashtags --");

        for (Map.Entry<String, Integer> entry : hashList.entrySet())
        {
            System.out.println(entry.getKey() + " → " + entry.getValue());
        }
    }

    public void annotateHashtags()
    {
        hashList.put("#PRESIDENT…", 0);
        hashList.put("#PRESIDENT…", 12);
    }
}
