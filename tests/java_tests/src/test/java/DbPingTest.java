import java.io.IOException;
import java.net.URISyntaxException;

import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.client.methods.HttpGet;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * @author senyasdr
 */
class DbPingTest extends DbAbstractTest {
    @Test
    void testPingDb() throws IOException, URISyntaxException, InterruptedException {
        //when
        HttpResponse resp = client.execute(new HttpGet(getBasicURI().setPath("/ping_db").build()));

        //then
        Assertions.assertEquals(HttpStatus.SC_OK, resp.getStatusLine().getStatusCode());
    }

    @Test
    void testPingDbStopped() throws IOException, URISyntaxException, InterruptedException {
        // given
        postgreDBContainer.close();

        //when
        HttpResponse resp = client.execute(new HttpGet(getBasicURI().setPath("/ping_db").build()));

        //then
        Assertions.assertEquals(HttpStatus.SC_SERVICE_UNAVAILABLE, resp.getStatusLine().getStatusCode());
        postgreDBContainer.start();
    }
}
