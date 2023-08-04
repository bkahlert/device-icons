
import ch.qos.logback.classic.Level
import com.bkahlert.kommons.logging.SLF4J
import com.bkahlert.kommons.logging.logback.Logback
import mdns.JmDNS
import mdns.ServiceInfo
import mdns.ServiceListener
import mdns.ServiceTypeListener
import mdns.serviceInfo
import model.Models
import javax.jmdns.JmDNS
import kotlin.concurrent.thread

val logger = SLF4J.getLogger("mdns-test")

fun main(args: Array<String>) {
    Logback.levels(
        "root" to Level.DEBUG,
        "io.netty" to Level.WARN,
        "javax.jmdns" to Level.WARN,
        "com.bkahlert.kommons.exec" to Level.WARN,
        "com.bkahlert.netmon.mdns" to Level.INFO,
        "com.bkahlert.netmon.mqtt" to Level.WARN,
        "com.bkahlert.netmon.net" to Level.INFO,
        "com.bkahlert.netmon.nmap" to Level.INFO,
    )

    listen()
//    publishServices()

    while (!Thread.interrupted()) {
        try {
            Thread.sleep(1000)
        } catch (e: InterruptedException) {
            Thread.currentThread().interrupt()
        }
    }

    logger.info("Done.")
}


private fun listen() {
    val serviceListener = object : ServiceListener {
        override fun serviceAdded(instance: JmDNS, type: String, name: String) {
            logger.info("Service added: $name.$type")
        }

        override fun serviceResolved(instance: JmDNS, type: String, name: String, info: ServiceInfo) {
            logger.info("Service resolved: $name.$type: $info")
        }

        override fun serviceRemoved(instance: JmDNS, type: String, name: String) {
            logger.info("Service removed: $name.$type")
        }
    }
    val serviceTypeListener = object : ServiceTypeListener {
        override fun serviceTypeAdded(instance: JmDNS, type: String) {
            logger.info("Service type added: $type")
            instance.addServiceListener(type, serviceListener)
        }

        override fun subTypeForServiceTypeAdded(instance: JmDNS, typeWithSubtype: String) {
            logger.info("Service sub type added: $typeWithSubtype")
        }
    }

    mdns.JmDNS().apply {
//        addServiceTypeListener(serviceTypeListener)
//        addServiceListener("_googlecast._tcp.local.", serviceListener)
    }

    fixServices()
}

private fun fixServices() {
    val jmDNS = mdns.JmDNS(name = "host-airportextreme5")
    logger.info("Registering services to fix")
    jmDNS.apply {
//        registerService(
//            javax.jmdns.ServiceInfo.create(
//                "_airportextreme5._tcp.local.",
//                "test_airportextreme5",
//                "",
//                0,
//                0,
//                0,
//                false,
//                ""
//            )
//        )
//        registerService(
//            ServiceInfoImpl(
//                "_tcp.local.",
//                "_airportextreme5",
//                "",
//                0,
//                0,
//                0,
//                false,
//                ""
//            )
//        )
//        registerService(
//            ServiceInfoImpl(
//                "_airportextreme5._tcp.local.",
//                "_airportextreme5",
//                "",
//                0,
//                0,
//                0,
//                false,
//                ""
//            )
//        )
//        registerService(
//            ServiceInfoImpl(
//                ".local.",
//                "",
//                "",
//                0,
//                0,
//                0,
//                false,
//                ""
//            )
//        )
    }
    thread {
        Thread.sleep(5000)
        logger.warn("Unregistering services to fix")
        jmDNS.unregisterAllServices()
    }
}


private fun publishServices() {
    val serviceGroups = buildMap {
        if (true) putAll(Models)


//        putAll(AllModels.apple_watch)
//        putAll(AllModels.appletv)
//        putAll(AllModels.emac)
//        putAll(AllModels.homepod)
//        putAll(AllModels.ibook)
//        putAll(AllModels.imac)
//        putAll(AllModels.imac_pro)
//        putAll(AllModels.ipad)
//        putAll(AllModels.iphone)
//        putAll(AllModels.ipod)
//        putAll(AllModels.mac_server_g3)
//        putAll(AllModels.macbook)
//        putAll(AllModels.macbook_air)
//        putAll(AllModels.macbookpro)
//        putAll(AllModels.macmini)
//        putAll(AllModels.macpro)
//        putAll(AllModels.macstudio)
//        putAll(AllModels.powerbook_g3)
//        putAll(AllModels.powerbook_g4)
//        putAll(AllModels.powermac_g3)
//        putAll(AllModels.powermac_g4)
//        putAll(AllModels.powermac_g5)
//        putAll(AllModels.xserve)
    }.mapValues { (name, model) ->
        listOf(
            serviceInfo(
                name = "test-$name",
                type = "_device-info._tcp.local.",
            ) {
                put("model", model)
            },
            serviceInfo(
                name = "test-$name",
                type = "_smb._tcp.local.",
                port = 445,
            ) {
                put("u", "pi")
                put("p", "pi")
            },
            serviceInfo(
                name = "test-$name",
                type = "_ssh._tcp.local.",
                port = 22,
            ),
            serviceInfo(
                name = "test-$name",
                type = "_sftp-ssh._tcp.local.",
                port = 22,
            ),
            serviceInfo(
                name = "test-$name",
                type = "_http._tcp.local.",
                port = 80,
            ) {
                put("path", "/unsecure")
                put("u", "pi")
                put("p", "pi")
            },
            serviceInfo(
                name = "test-$name",
                type = "_https._tcp.local.",
                port = 443,
            ) {
                put("path", "/secure")
                put("u", "pi")
                put("p", "pi")
            },
        )
    }

    val serviceCount = serviceGroups.entries.sumOf { (_, services) -> services.size }
    logger.info("Testing ${serviceGroups.size} groups with a total of $serviceCount services...")

    serviceGroups.forEach { (name, services) ->
        val host = "host-$name"
        logger.info("Publishing ${services.size} services for $host...")
        JmDNS(name = host).apply {
            services.forEach { service ->
                registerService(service)
            }
        }
    }
}
