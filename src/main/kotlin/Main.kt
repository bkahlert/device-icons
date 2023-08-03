import ch.qos.logback.classic.Level
import com.bkahlert.kommons.logging.SLF4J
import com.bkahlert.kommons.logging.logback.Logback
import mdns.HostServices
import mdns.serviceInfo

/**
 * @see <a href="file:///System/Library/CoreServices/PlatformSupport.plist">PlatformSupport.plist</a>
 */
val platformSupportModels = listOf(
    "MacBookPro14,2",
    "MacBookPro14,3",
    "MacBook10,1",
    "MacBookPro14,1",
    "MacBookPro15,2",
    "iMac18,1",
    "iMac18,2",
    "iMac18,3",
    "iMacPro1,1",
    "iMac19,1",
    "iMac19,2",
    "MacBookAir8,2",
    "MacBookAir8,1",
    "MacBookPro16,1",
    "MacPro7,1",
    "Macmini8,1",
    "iMac20,1",
    "iMac20,2",
    "MacBookPro15,4",
    "MacBookPro16,2",
    "MacBookPro16,4",
    "MacBookPro16,3",
    "MacBookAir9,1",
    "MacBookPro15,1",
    "MacBookPro15,3",
)

/**
 * `ls /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/DeviceSupport/ | pbcopy`
 */
val deviceSupport = listOf(
    "11.0", "11.1", "11.2", "11.3", "11.4",
    "12.0", "12.1", "12.2", "12.3", "12.4",
    "13.0", "13.1", "13.2", "13.3", "13.4", "13.5", "13.6", "13.7",
    "14.0", "14.1", "14.2", "14.3", "14.4", "14.5",
    "15.0", "15.2", "15.4", "15.5",
    "16.0", "16.1", "16.4",
).flatMap { listOf("iPhone$it", "iPad$it", "iPadPro$it") }
    .map { it.replace('.', ',') }

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

    /**
     * Sources:
     * - /System/Library/CoreServices/PlatformSupport.plist
     */
    val models = listOf(
        "AirPortExtreme5",
        "MacBookPro15,1",
        "Mac14,13",
        "iPhone1,1",
        "iPhone10,3",
        "RaspberryPi",
        "RaspberryPi3",
        "RaspberryPi3B",
        "HP-LaserJet-5200",
        "CustomServer2019",
        "PC",
        "MacMini",
    )

    val buildSet = buildSet {
        addAll(platformSupportModels)
        addAll(deviceSupport)
        addAll(models)
    }
    val hostServices = buildSet.map { model ->
        HostServices("host-$model") {
            add(
                serviceInfo(
                    name = "test-$model",
                    type = "_device-info._tcp.local.",
                    text = "model=$model",
                )
            )
            add(
                serviceInfo(
                    name = "test-$model",
                    type = "_smb._tcp.local.",
                    port = 445,
                ),
            )
        }
    }

    val hostCount = hostServices.size
    val serviceCount = hostServices.sumOf { it.services.size }
    logger.info("Testing $hostCount hosts with a total of $serviceCount services...")

    while (!Thread.interrupted()) {
        try {
            Thread.sleep(1000)
        } catch (e: InterruptedException) {
            Thread.currentThread().interrupt()
        }
    }

    logger.info("Done.")
}
