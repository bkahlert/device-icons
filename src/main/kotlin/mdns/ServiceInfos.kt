package mdns

import javax.jmdns.ServiceInfo

/**
 * Kotlin-idiomatic [ServiceInfo.create] variant.
 *
 * @param name unqualified service instance name, such as <code>foobar</code>
 * @param type fully qualified service type name, such as <code>_http._tcp.local.</code>.
 * @param subtype service subtype see draft-cheshire-dnsext-dns-sd-06.txt chapter 7.1 Selective Instance Enumeration
 * @param port the local port on which the service runs
 * @param weight weight of the service
 * @param priority priority of the service
 * @param persistent if <code>true</code> ServiceListener.resolveService will be called whenever new information is received.
 * @param text string describing the service
 * @return new service info
 */
fun serviceInfo(
    name: String,
    type: String,
    subtype: String = "",
    port: Int = 0,
    weight: Int = 0,
    priority: Int = 0,
    persistent: Boolean = false,
    text: String = "",
): ServiceInfo = ServiceInfo.create(type, name, subtype, port, weight, priority, persistent, text)
