package basic

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._
import scala.collection.mutable.ArrayBuffer
import scala.sys.process._
import java.util.Calendar

class MyStockPerf extends Simulation {

 
 

  /******************************************************************/
  /******************************************************************/
  /***************************   HTTPCONF   **************************/
  /******************************************************************/
  /******************************************************************/
  /******************************************************************/

  val baseUrl = http
    .baseURL("http://localhost:5000/stock")

 
  /******************************************************************/
  /******************************************************************/
  /***************************   FEEDS   ****************************/
  /******************************************************************/
  /******************************************************************/
  /******************************************************************/

  val feedImeiPsav = csv("imeiPsav.csv").random // imei,gencod,psav
  val feedImeiPsavPersistent = csv("imeiPsavPersistent.csv").random // imei,gencod,psav, que les psav qui ne servent pas au transfert de stock
  val feedPsav = csv("psav.csv").random 
  val feedPsavTransfert = csv("psavTransfert.csv").random

  val feedEtat = new Feeder[String] {

    private val RNG = new scala.util.Random

    override def hasNext = true

    override def next: Map[String, String] = {
      val rand: Int = RNG.nextInt(1)
      var etat = "D"
      if (rand == 1) {
        etat = "K"
      }
      Map("etat" -> etat)
    }
  }

   val feedBodyStock = new Feeder[String] {

    private val RNG = new scala.util.Random

    private def randInt(a: Int, b: Int) = RNG.nextInt(b - a) + a

    override def hasNext = true

    override def next: Map[String, String] = {
      val fakeIMEI: Int = randInt(1, 100000000)
      var body: String = """{"etat" : "D", "gencod": "3526356039329",  "imei" : """ + "\"" + fakeIMEI + "\"" + "}"

      Map("bodystock" -> body.toString())
    }
  }
 
  //fin feeds

  /******************************************************************/
  /******************************************************************/
  /**********************    SCENARIO    ****************************/
  /******************************************************************/
  /******************************************************************/

  //les scenarios

  val scnBulkCheckImei = scenario("Interrogation en masse")
    .feed(feedPsav)
    .exec(
      http("Interrogation en masse")
        .get("/${psav}")
        .check(status.is(200)))

  val scnCheckImei = scenario("Check d'un imei")
    .feed(feedImeiPsav)
    .exec(
      http("Check d'un imei")
        .get("/${psav}/imei/${imei}")
        .check(status.in(200,404)))

  val scnCheckAndUpdateUpdateImei = scenario("Check et update imei")
    .feed(feedImeiPsavPersistent)
    .feed(feedEtat)
    .exec(
      http("Check d'un imei")
        .get("/${psav}/imei/${imei}")
        .check(status.in(200)))
    .exec(
      http("Changement d'état d'un imei")
        .put("/${psav}/imei/${imei}?etat=${etat}")
        .check(status.is(204)))

  val scnInsertImei = scenario("Insertion en stock")
    .feed(feedPsav)
    .feed(feedBodyStock)
    .exec( // voir comment on fait une boucle
      http("Insertion en stock")
        .post("/${psav}/imei")
        .body(StringBody("${bodystock}")).asJSON
        .check(status.is(201)))

  val scnTransfertActivite = scenario("Transfert activité")
    .feed(feedPsavTransfert)
    .feed(feedPsav)
    .exec(
      http("Transfert activité")
        .post("/${psavTransfert}/transfert/${psav}?type=total")
        .check(status.is(200)))

  val scnReappro = scenario("Réapprovisionnement")
    .exec(
      http("Réapprovisionnement")
        .post("/reappro")
        .check(status.is(200)))
 //fin scenario   

  /******************************************************************/
  /******************************************************************/
  /**********************    LANCEMENT    ***************************/
  /******************************************************************/
  /******************************************************************/

  //lancement des tests
 
  //la duree du test en seconde
  val dureeTest = 60

  val nbBulkCheckParSeconde = 1
  val nbCheckImeiParSeconde = 3
  val nbUpdateImeiParSeconde = 1
  val nbInsertImeiParSeconde = 1
  val nbTransfertParSeconde = 0.5
  val nbReapproParSeconde = 0.2
 
  setUp(scnBulkCheckImei.inject(rampUsers(dureeTest * nbBulkCheckParSeconde) over (dureeTest seconds))).protocols(baseUrl)
  setUp(scnCheckImei.inject(rampUsers(dureeTest * nbCheckImeiParSeconde) over (dureeTest seconds))).protocols(baseUrl)
  setUp(scnCheckAndUpdateUpdateImei.inject(rampUsers(dureeTest * nbUpdateImeiParSeconde) over (dureeTest seconds))).protocols(baseUrl)
  setUp(scnInsertImei.inject(rampUsers(dureeTest * nbInsertImeiParSeconde) over (dureeTest seconds))).protocols(baseUrl)
  setUp(scnTransfertActivite.inject(rampUsers(1) over (3 seconds))).protocols(baseUrl)
  setUp(scnReappro.inject(rampUsers(1) over (60 seconds))).protocols(baseUrl)
 
 

// Revoir les deux derniers cas
  //setUp(
  //scn.inject(
  //  nothingFor(4 seconds), // 1
  //  atOnceUsers(10), // 2
  //  rampUsers(10) over(5 seconds), // 3
  //  constantUsersPerSec(20) during(15 seconds), // 4
  //  constantUsersPerSec(20) during(15 seconds) randomized, // 5
  //  rampUsersPerSec(10) to(20) during(10 minutes), // 6
  //  rampUsersPerSec(10) to(20) during(10 minutes) randomized, // 7
  //  splitUsers(1000) into(rampUsers(10) over(10 seconds)) separatedBy(10 seconds), // 8
  //  splitUsers(1000) into(rampUsers(10) over(10 seconds)) separatedBy(atOnceUsers(30)), // 9
  //  heavisideUsers(1000) over(20 seconds) // 10
  //  ).protocols(httpConf)
  //)

}

