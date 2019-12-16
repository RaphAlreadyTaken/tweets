package fr.ceri.entities;

import org.apache.http.HttpHost;
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.action.search.SearchResponse;
import org.elasticsearch.action.search.SearchScrollRequest;
import org.elasticsearch.client.RequestOptions;
import org.elasticsearch.client.RestClient;
import org.elasticsearch.client.RestClientBuilder;
import org.elasticsearch.client.RestHighLevelClient;
import org.elasticsearch.common.unit.TimeValue;
import org.elasticsearch.index.query.QueryBuilders;
import org.elasticsearch.search.Scroll;
import org.elasticsearch.search.SearchHit;
import org.elasticsearch.search.builder.SearchSourceBuilder;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class ElasticQuery
{
    private RestHighLevelClient restHighLevelClient;

    public ElasticQuery(String host, int port, String protocol)
    {
        RestClientBuilder builder = RestClient.builder(new HttpHost(host, port, protocol));
        restHighLevelClient = new RestHighLevelClient(builder);
    }

    public SearchRequest buildElasticQuery(String[] includes, String[] excludes)
    {
        SearchRequest request = new SearchRequest();

        SearchSourceBuilder searchSourceBuilder = new SearchSourceBuilder();
        searchSourceBuilder.fetchSource(includes, excludes).query(QueryBuilders.matchAllQuery());

        request.source(searchSourceBuilder).scroll(TimeValue.timeValueMinutes(2L));

        return request;
    }

    public List<SearchHit> sendElasticQuery(SearchRequest request) throws IOException
    {
        Scroll scroll = new Scroll(TimeValue.timeValueMinutes(1L));
        request.scroll(scroll);

        SearchResponse response = restHighLevelClient.search(request, RequestOptions.DEFAULT);

        String scrollId = response.getScrollId();
        SearchHit[] hitsBase = response.getHits().getHits();
        List<SearchHit> hits = new ArrayList<>(Arrays.asList(hitsBase));

        while (hitsBase.length > 0)
        {
            SearchScrollRequest scrollRequest = new SearchScrollRequest(scrollId);
            scrollRequest.scroll(scroll);
            response = restHighLevelClient.searchScroll(scrollRequest, RequestOptions.DEFAULT);
            scrollId = response.getScrollId();

            hitsBase = response.getHits().getHits();
            hits.addAll(Arrays.asList(hitsBase));
        }

        restHighLevelClient.close();

        return hits;
    }
}
