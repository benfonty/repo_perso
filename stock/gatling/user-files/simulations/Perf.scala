package basic

import com.excilys.ebi.gatling.core.Predef._
import com.excilys.ebi.gatling.http.Predef._
import com.excilys.ebi.gatling.jdbc.Predef._
import com.excilys.ebi.gatling.http.Headers.Names._
import akka.util.duration._
import bootstrap._
import scala.collection.mutable.ArrayBuffer
import com.excilys.ebi.gatling.core.structure.ScenarioBuilder
import scala.sys.process._
import java.util.Calendar

class Perf extends Simulation {

 
  val baseUrl = "localhost:5000/stock/"

  //la duree du test en seconde
  val dureeTest = 60

  /******************************************************************/
  /******************************************************************/
  /***************************   HTTPCONF   **************************/
  /******************************************************************/
  /******************************************************************/
  /******************************************************************/

  val httpConfServicenc7000 = httpConfig
    .baseURL(urlServiceNC700)

  val httpConfApi = httpConfig
    .baseURL(urlWebApiPasserelle)

  val httpConfServiceSAIO = httpConfig
    .baseURL(urlServiceSAIO)

  val httpConfServiceCustomerOffer = httpConfig
    .baseURL(urlServiceCustomerOffer)

  val httpConfServiceRadiusOffer = httpConfig
    .baseURL(urlServiceRadiusOffer)

  val httpConfServiceHealthcheck = httpConfig
    .baseURL(urlServiceHealthcheck)

  val httpConfServiceNotiferMouvementCT = httpConfig
    .baseURL(urlNotifierMouvementCT)

  /******************************************************************/
  /******************************************************************/
  /***************************   FEEDS   ****************************/
  /******************************************************************/
  /******************************************************************/
  /******************************************************************/

  //feed utilisee pour getFixCustomerControlData  et getMobileCustomerControlData et CustomerOffer
  val feedInfoSRVID = csv("PA_SRVID.csv").random
  val feedInfoMSISDN = csv("PA_MSISDN.csv").random
  val feedInfoEID = csv("PA_EID.csv").random

  //pour les TOKEN
  val feedPersonToken = csv("extractToken.csv").random

  //pour SAIO
  val feedInfoPA = csv("PA.csv").random

  // pour radius offer
  val rngCustomSRVID = new scala.util.Random

  val feedInfoCustomSRVID = new Feeder[String] {

    private val RNG = new scala.util.Random

    private def randInt(a: Int, b: Int) = RNG.nextInt(b - a) + a

    override def hasNext = true

    override def next: Map[String, String] = {
      val srvid = randInt(100000, 999999).toString()

      Map("customsrvid" -> srvid.toString())
    }
  }

  val feedInfoCustomOffre = new Feeder[String] {

    private val RNG = new scala.util.Random

    private def randInt(a: Int, b: Int) = RNG.nextInt(b - a) + a

    override def hasNext = true

    override def next: Map[String, String] = {
      val customoffre: Int = randInt(1, 10)
      var body: String = """{"radiusOffers" : [ """
      for (i <- 0 to customoffre) {
        if (i != customoffre) {
          body = body + """"""" + lstRadiusOffer(i).toString() + """"""" + " , "
        } else {
          body = body + """"""" + lstRadiusOffer(i).toString() + """""""
        }
      }
      body = body + " ]}"

      Map("bodyRadiusOffer" -> body.toString())
    }
  }

  val feedNumVoip = new Feeder[String] {

    private val RNG = new scala.util.Random

    private def randInt(a: Int, b: Int) = RNG.nextInt(b - a) + a

    override def hasNext = true

    override def next: Map[String, String] = {
      val srvid = randInt(1, 999999999).toString()

      Map("numvoip" -> srvid.toString())
    }
  }

  val feedPfsPourNotifier = csv("notifierMouvement.csv").circular

  //fin feeds

  /******************************************************************/
  /******************************************************************/
  /**********************    SCENARIO    ****************************/
  /******************************************************************/
  /******************************************************************/

  //les scenarios

  //NC7000 PSWG
  val scnNC7000MobileAvecMsisdn = scenario("[PSWG] getCustomerControlData avec msisdn")
    .feed(feedInfoMSISDN)
    .exec(
      http("[PSWG] CustomerControlData avec msisdn")
        .get("/MSISDN/@${pointAccesDares.0.cle.valeur}")
        .check(status.is(200)))

  val scnNC7000MobileAvecEid = scenario("getCustomerControlData avec eid")
    .feed(feedInfoEID)
    .exec(
      http("[PSWG] CustomerControlData avec eid")
        .get("/EID/@${pointAccesDares.0.cle.valeur}")
        .check(status.is(200)))

  val scnNC7000FixeAvecSrvId = scenario("getCustomerControlData avec srv_id")
    .feed(feedInfoSRVID)
    .exec(
      http("[PSWG] CustomerControlData avec srv_id")
        .get("/srv_id/@${pointAccesDares.0.cle.valeur}")
        .check(status.is(200)))

  // NC70003A GET 
  val scnNC70003aMobileGET = scenario("[TOKEN] GET TOKEN")
    .feed(feedPersonToken)
    .exec(
      http("[TOKEN-GET] get(oid)")
        .get("/tokens/getToken?oid=${_id}")
        .check(status.is(204)))

  //NC70003A SAVE
  val scnNC70003aMobileSAVE = scenario("[TOKEN] SAVE TOKEN")
    .feed(feedPersonToken)
    .exec(
      http("[TOKEN-SAVE] getInfo(Token)")
        .get("/tokens/saveToken?typePA=${accessPoint.type}&valuePA=${accessPoint.value}&applicationId=${applicationId}&personNumber=${personNumber}")
        .check(status.is(204)))

  //SAIO
  val scnSAIO = scenario("[SAIO] appel Saio")
    .feed(feedInfoPA)
    .exec(
      http("[SAIO] appel Saio")
        .get("/${pointAccesDares.0.cle.type}/@${pointAccesDares.0.cle.valeur}/saio")
        .check(status.is(200)))

  //CustomerOffer        
  val scnCustomerOfferAvecMsisdn = scenario("[CUSTOMEROFFER] getCustomerOffer avec msisdn")
    .feed(feedInfoMSISDN)
    .exec(
      http("[CUSTOMEROFFER] CustomerOffer avec msisdn")
        .get("/msisdn/@${pointAccesDares.0.cle.valeur}/offer")
        .check(status.is(200)))

  val scnCustomerOfferAvecEid = scenario("[CUSTOMEROFFER] getCustomerOffer avec eid")
    .feed(feedInfoEID)
    .exec(
      http("[CUSTOMEROFFER] CustomerOffer avec eid")
        .get("/eid/@${pointAccesDares.0.cle.valeur}/offer")
        .check(status.is(200)))

  val scnCustomerOfferAvecSrvId = scenario("[CUSTOMEROFFER] getCustomerOffer avec srv_id")
    .feed(feedInfoSRVID)
    .exec(
      http("[CUSTOMEROFFER] CustomerOffer avec srv_id")
        .get("/srv_id/@${pointAccesDares.0.cle.valeur}/offer")
        .check(status.is(200)))

  //RadiusOffer        
  val scnRadiusOfferPost = scenario("[RADIUSOFFER] postRadiusOffers")
    .feed(feedInfoSRVID)
    .feed(feedInfoCustomSRVID)
    .feed(feedInfoCustomOffre)
    .doIfOrElse(indexPostRadiusOffer.getAndIncrement() % proportionPostRadiusOffer == 0) {
      exec(
        http("[RADIUSOFFER] postRadiusOffers")
          .post("/srv_id/@${pointAccesDares.0.cle.valeur}/offer/radiusoffers")
          .body("${bodyRadiusOffer}").asJSON
          .check(status.is(200)))
    } {
      exec(
        http("[RADIUSOFFER] postRadiusOffers")
          .post("/srv_id/@${customsrvid}/offer/radiusoffers")
          .body("${bodyRadiusOffer}").asJSON
          .check(status.is(200)))
    }

  val scnRadiusOfferPut = scenario("[RADIUSOFFER] putRadiusOffers")
    .feed(feedInfoSRVID)
    .feed(feedInfoCustomOffre)
    .exec(
      http("[RADIUSOFFER] putRadiusOffers")
        .put("/srv_id/@${pointAccesDares.0.cle.valeur}/offer/radiusoffers")
        .body("${bodyRadiusOffer}").asJSON
        .check(status.is(200)))

  val format = new java.text.SimpleDateFormat("dd-MM-yyyy")
  format.format(new java.util.Date())
  val toto = format.parse("21-03-2011");

  //NOTIFIER MOUVEMENT CT 
  val scnNotifierMouvementCT = scenario("[NOTIFIER MOUVEMENT CT] notifier Mouvement CT")
    .feed(feedPfsPourNotifier)
    .feed(feedNumVoip)
    .exec(
      http("[NOTIFIER MOUVEMENT CT] post mouvement")
        .post("")
        .fileBody("notifierMouvement", Map("date" -> new java.text.SimpleDateFormat("yyyyMMddHHmmss").format(new java.util.Date()), "numpfs" -> "${_id}", "numprsuser" -> "${infosPersonUser.noPerson}", "numprspayeur" -> "${infosPersonPayer.noPerson}", "numprsowner" -> "${infosPersonOwner.noPerson}", "numVoip" -> "${numvoip}"))
        .check(status.is(200)))

  //HEALTHCHECK   
  val scnHealthcheck = scenario("HEALTHCHECK")
    .exec(
      http("HEALTHCHECK")
        .get("?wait=true")
        .check(status.is(200)))
  //fin scenario   

  /******************************************************************/
  /******************************************************************/
  /**********************    LANCEMENT    ***************************/
  /******************************************************************/
  /******************************************************************/

  //lancement des tests

  if (testPSWG) {
    val nbUsers = dureeTest * nbUserParSecondeNC7000PSWG
    setUp(scnNC7000MobileAvecMsisdn.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfServicenc7000))
    setUp(scnNC7000MobileAvecEid.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfServicenc7000))
    setUp(scnNC7000FixeAvecSrvId.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfServicenc7000))
  }

  if (test3A_get) {
    val nbUsers = dureeTest * nbUserParSecondeNC70003A_get
    setUp(scnNC70003aMobileGET.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfApi))
  }

  if (test3A_save) {
    val nbUsers = dureeTest * nbUserParSecondeNC70003A_save
    setUp(scnNC70003aMobileSAVE.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfApi))
  }

  if (testSAIO) {
    val nbUsers = dureeTest * nbUserParSecondeSAIO
    setUp(scnSAIO.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfServiceSAIO))
  }

  if (testCustomerOffer) {
    val nbUsers = dureeTest * nbUserParSecondeCustomerOffer
    setUp(scnCustomerOfferAvecMsisdn.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfServiceCustomerOffer))
    setUp(scnCustomerOfferAvecEid.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfServiceCustomerOffer))
    setUp(scnCustomerOfferAvecSrvId.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfServiceCustomerOffer))
  }

  if (testPostRadiusOffer) {
    val nbUsers = dureeTest * nbUserParSecondeRadiusOffer
    setUp(scnRadiusOfferPost.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfServiceRadiusOffer))
  }

  if (testPutRadiusOffer) {
    val nbUsers = dureeTest * nbUserParSecondeRadiusOffer
    setUp(scnRadiusOfferPut.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfServiceRadiusOffer))
  }

  if (testHealthcheck) {
    val nbUsers = dureeTest * nbUserParSecondeHealthcheck
    setUp(scnHealthcheck.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfServiceHealthcheck))
  }

  if (testNotifierMouvementCT) {
    val nbUsers = dureeTest * nbUserParSecondeNotifierMouvementCT
    setUp(scnNotifierMouvementCT.users(nbUsers).ramp(dureeTest).protocolConfig(httpConfServiceNotiferMouvementCT))
  }

  val hello = new Thread(new Runnable {
    def run() {
      Thread.sleep(dureeAvantLancementProvisonning)
      kshLancementProvisionning.run()
    }
  })

  if (lancementProvisonning) {
    hello.start
  }
  //

}

