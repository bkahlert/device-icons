package model

/**
 * Models that work nicely together with device-info.
 */
data object Models : Iterable<Pair<String, String>> {

    data object Devices : Iterable<Pair<String, String>> {
        /**
         * "AirPods Pro (2nd generation)"
         * - Kind: Mac
         */
        const val InEar = "Device1,8212"

        /**
         * "Beats Studio Pro"
         * - Kind: Mac
         */
        const val OverEar = "Device1,8215"

        /*
        add("AirPods1,3")
        add("AirPodsMax1,1")
        add("AirPodsPro1,1")
        add("Device1,8211")
        add("Device1,21760") // AirTag
         */
        override fun iterator(): Iterator<Pair<String, String>> =
            listOf(::InEar, ::OverEar)
                .map { "Device-${it.name}" to it.get() }
                .iterator()
    }

    data object AirPort : Iterable<Pair<String, String>> {
        /**
         * Kind: Mac
         */
        const val Mac = "AirPort4"

        /**
         * Kind: Time Capsule
         */
        const val TimeCapsule = "AirPort6"

        /**
         * - Kind: AirPort Extreme
         */
        const val Flat = "AirPort5"

        /**
         * - Kind: AirPort Extreme
         */
        const val Tower = "AirPort7"
        override fun iterator(): Iterator<Pair<String, String>> =
            listOf(::Mac, ::TimeCapsule, ::Flat, ::Tower)
                .map { "AirPort-${it.name}" to it.get() }
                .iterator()
    }

    data object Mac : Iterable<Pair<String, String>> {
        /**
         * Kind: Mac
         */
        const val Remote = "ATVRemote1,1"

        /**
         * Kind: Mac
         */
        const val RemoteTouch = "ATVRemote1,2"

        /**
         * Kind: Mac
         */
        const val Pencil = "Pencil1,1"

        /**
         * The black Mac Pro cylinder
         * - Kind: Mac
         * - Color: Black
         */
        const val Cylinder = "MacPro6,1"

        /**
         * Tower Mac
         * - Kind: Mac
         */
        const val TowerClassic = "MacPro5,1"

        /**
         * Tower Mac
         * - Kind: Mac
         */
        const val Tower = "MacPro7,1@ECOLOR=225,225,223"

        /**
         * Rack Mac
         * - Kind: Mac
         */
        const val Rack = "MacPro7,1@ECOLOR=226,226,224"
//        const val Rack = "Mac14,8@ECOLOR=1"

        /**
         * Server Mac
         * - Kind: Mac
         */
        const val Server = "Xserve3,1"

//        add("VMWare")
//        add("VirtualMac")

        data object Mini : Iterable<Pair<String, String>> {

            /**
             * Mac mini
             * - Kind: Mac
             * - Color: Black
             */
            const val Black = "Macmini8,1"

            /**
             * Mac mini
             * - Kind: Mac
             * - Color: Silver
             */
            const val Silver = "Macmini9,1"
            override fun iterator(): Iterator<Pair<String, String>> =
                listOf(::Black, ::Silver)
                    .map { it.name to it.get() }
                    .iterator()
        }

        override fun iterator(): Iterator<Pair<String, String>> =
            listOf(::Remote, ::RemoteTouch, ::Pencil, ::Cylinder, ::TowerClassic, ::Tower, ::Rack, ::Server)
                .map { "Mac-${it.name}" to it.get() }
                .plus(Mini.toList().map { "Mac-Mini-${it.first}" to it.second })
                .iterator()
    }

    override fun iterator(): Iterator<Pair<String, String>> =
        (Devices + AirPort + Mac).iterator()
}
