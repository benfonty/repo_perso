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
      val rand: Int = RNG.nextInt(10)
      var etat = "D"
      if (rand >= 5) {
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
    .pause(3 seconds)
    .exec(
      http("Changement d'état d'un imei")
        .put("/${psav}/imei/${imei}?etat=${etat}")
        .check(status.is(204)))

  val scnUpdateUpdateImei = scenario("update imei")
    .feed(feedImeiPsavPersistent)
    .feed(feedEtat)
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
 
 setUp(
  // check and update = 8000 par jour = 2,5 par seconde pour faire un jour en une heure
  // 2000 pendant 20 minutes, 3000 pendant 10 minutes, le tout deux fois, pour reproduire les pics du midi et du soir.
  scnCheckAndUpdateUpdateImei.inject(
    constantUsersPerSec(2) during(20 minutes) randomized,
    constantUsersPerSec(5) during(10 minutes) randomized,
    constantUsersPerSec(2) during(20 minutes) randomized,
    constantUsersPerSec(5) during(10 minutes) randomized
    ).protocols(baseUrl),
  // bulk check 1 toutes les trentes secondes
   scnBulkCheckImei.inject(
    splitUsers(120) into(atOnceUsers(1)) separatedBy(30 seconds)
    ).protocols(baseUrl),
   // insert imei (200 toutes les 5 minutes)
   scnInsertImei.inject(
    splitUsers(2400) into(rampUsers(200) over(4 seconds)) separatedBy(5 minutes)
    ).protocols(baseUrl),
   // transfert 1 par tranche de 20 minutes
    scnTransfertActivite.inject(
    nothingFor(10 minutes),
    atOnceUsers(1),
    nothingFor(20 minutes),
    atOnceUsers(1),
    nothingFor(20 minutes),
    atOnceUsers(1)
    ).protocols(baseUrl),
  // reappro : 1 pendant les moments calmes 
   scnReappro.inject(
    nothingFor(40 minutes),
    atOnceUsers(1)
    ).protocols(baseUrl)
  )

}

