package mdns

import com.bkahlert.kommons.Program
import com.bkahlert.kommons.logging.SLF4J
import javax.jmdns.JmDNS
import javax.jmdns.ServiceInfo

class HostServices(
    val hostname: String,
    val services: List<ServiceInfo>,
) : AutoCloseable {
    private val logger by SLF4J

    constructor(
        hostname: String,
        init: MutableList<ServiceInfo>.() -> Unit,
    ) : this(hostname, buildList(init))

    val jmdns = JmDNS.create(null, hostname).apply {
        services.forEach {
            logger.info("Registering service $it")
            registerService(it)
        }
    }

    init {
        Program.onExit { close() }
    }

    override fun close() {
        jmdns.apply { unregisterAllServices() }.close()
    }

}
