import java.io.IOException;
import java.net.URISyntaxException;
import java.time.Duration;
import java.util.Objects;
import java.lang.Thread;

import com.google.gson.Gson;
import org.apache.http.HttpHost;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.containers.wait.strategy.HttpWaitStrategy;

/**
 * @author senyasdr
 */
public abstract class DbAbstractTest {

    protected static Network network;
    protected static GenericContainer<?> appContainer;
    protected static PostgreSQLContainer<?> postgreDBContainer;
    protected static CloseableHttpClient client;
    protected static Gson gson = new Gson();
    protected static String appHost;
    protected static Integer appPort;

    @BeforeEach
    void setUp() throws IOException, URISyntaxException, InterruptedException {

        String image = System.getenv("IMAGE_NAME");
        Objects.requireNonNull(image, "Env var IMAGE_NAME (app docker image) not provided");

        network = Network.newNetwork();
        postgreDBContainer = new PostgreSQLContainer<>("postgres:12.8")
                .withDatabaseName("testdb")
                .withUsername("testuser")
                .withPassword("testpassword")
                .withNetwork(network)
                .withNetworkAliases("testnet");
        postgreDBContainer.start();

        appContainer = new GenericContainer<>(image);
        // jdbc:postgresql://hosts/database + user + password
        appContainer.addEnv("POSTGRES_HOSTS", String.join(",", postgreDBContainer.getNetworkAliases()));
        appContainer.addEnv("POSTGRES_DB", postgreDBContainer.getDatabaseName());
        appContainer.addEnv("POSTGRES_USER", postgreDBContainer.getUsername());
        appContainer.addEnv("POSTGRES_PWD", postgreDBContainer.getPassword());
        appContainer.addEnv("AUTH_DISABLED", Boolean.TRUE.toString());
        appContainer.withNetwork(network);
        appContainer.withStartupTimeout(Duration.ofSeconds(30));
        appContainer.addExposedPort(8080);
        /*appContainer.waitingFor(new HttpWaitStrategy()
                .forStatusCode(200)
                .forPort(8080)
                .forPath("/ping")
                .withStartupTimeout(Duration.ofSeconds(40)));*/
        appContainer.start();
        Thread.sleep(1000);

        appHost = appContainer.getContainerIpAddress();
        appPort = appContainer.getMappedPort(8080);

        RequestConfig config = RequestConfig.custom()
                .setConnectTimeout(3 * 1000)
                .setConnectionRequestTimeout(3 * 1000)
                .setSocketTimeout(3 * 1000).build();
        client = HttpClientBuilder.create().setDefaultRequestConfig(config).build();
    }

    @AfterEach
    void tearDown() {
        safeClose(appContainer);
        safeClose(postgreDBContainer);
        safeClose(network);
        safeClose(client);
    }

    void safeClose(AutoCloseable entity) {
        try {
            if (entity != null) {
                entity.close();
            }
        } catch (Exception e) {
            // ignored
        }
    }

    protected URIBuilder getBasicURI() {
        return new URIBuilder()
                .setHost(appHost)
                .setPort(appPort)
                .setScheme(HttpHost.DEFAULT_SCHEME_NAME);
    }
}