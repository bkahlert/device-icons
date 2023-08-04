package mdns

import io.kotest.matchers.shouldBe
import org.junit.jupiter.api.Test
import javax.jmdns.ServiceInfo

class JmDNSKtTest {

    @Test
    fun service_info() {
        serviceInfo(
            name = "service-name",
            type = "_device-info._tcp.local.",
            text = "model=Xserve",
        ) shouldBe ServiceInfo.create(
            "_device-info._tcp.local.",
            "service-name",
            0,
            "model=Xserve",
        )
    }

    @Test
    fun service_info2() {
        ServiceInfo.create(
            "_device-info._tcp.local.",
            "service-name",
            0,
            "model=Xserve",
        ) shouldBe ServiceInfo.create(
            "_device-info._tcp.local.",
            "service-name",
            0,
            "model=Xserve",
        )
    }
}
