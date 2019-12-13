package fr.ceri;

import fr.ceri.entities.ElasticQuery;
import fr.ceri.entities.HashtagProcessor;
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.search.SearchHit;

import java.io.IOException;
import java.util.List;

public class Main
{
    public static void main(String[] args) throws IOException
    {
        String field = "hashtags";

        ElasticQuery query = new ElasticQuery("localhost", 9200, "http");
        SearchRequest request = query.buildElasticQuery(new String[]{field}, null);
        List<SearchHit> hits = query.sendElasticQuery(request);

        HashtagProcessor proc = new HashtagProcessor();
        proc.convertToHashtagMap(hits, field);
        proc.annotateHashtags();
        proc.displayHashtagMap();
    }
}
